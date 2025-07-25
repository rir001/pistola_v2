from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from .models import Object, Person, Loan, Kind
from django.http import JsonResponse
from django.db.models import Q

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('loan_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def loan_dashboard(request):
    active_loans = Loan.objects.filter(return_date__isnull=True)
    available_objects = Object.objects.exclude(loan__return_date__isnull=True)
    recent_loans = Loan.objects.all().order_by('-loan_date')[:10]

    context = {
        'active_loans': active_loans,
        'available_objects': available_objects,
        'recent_loans': recent_loans,
    }
    return render(request, 'loans/dashboard.html', context)

@login_required
def create_loan(request):
    if request.method == 'POST':
        object_code = request.POST.get('object_code')
        person_rut = request.POST.get('person_rut')

        try:
            obj = Object.objects.get(code=object_code)

            # Crear persona si no existe
            person, created = Person.objects.get_or_create(
                RUT=person_rut,
                defaults={'first_name': '', 'last_name': '', 'email': ''}
            )

            if person.get_debt() > 0:
                messages.error(request, 'Esta persona tiene deuda y no puede pedir más objetos.')
                return redirect('loan_dashboard')

            if created:
                messages.info(request, f'Nueva persona registrada con RUT: {person_rut}')

            # Verificar que el objeto no esté prestado
            if Loan.objects.filter(object=obj, return_date__isnull=True).exists():
                messages.error(request, 'Este objeto ya está prestado')
                return redirect('loan_dashboard')

            # Crear el préstamo
            loan = Loan.objects.create(
                object=obj,
                person=person,
                loan_date=timezone.now()
            )

            messages.success(request, f'Préstamo creado exitosamente: {obj.name} a {person.RUT}')
            return redirect('loan_dashboard')

        except Object.DoesNotExist:
            messages.error(request, 'Objeto no encontrado')
        except Exception as e:
            messages.error(request, f'Error al crear el préstamo: {str(e)}')

    return redirect('loan_dashboard')

@login_required
def return_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    person = loan.person
    debt = person.get_debt()

    print(debt)

    if request.method == 'POST':
        if debt > 0:
            # Si GET, mostrar confirmación con deuda
            return render(request, 'loans/return_confirm.html', {
                'loan': loan,
                'person': person,
                'debt': debt,
            })

        if loan.return_date is None:
            loan.return_date = timezone.now()
            loan.save()
            messages.success(request, f'Préstamo devuelto: {getattr(loan.object, "name", "Objeto desconocido")}')
        else:
            messages.warning(request, 'Este préstamo ya fue devuelto')
        return redirect('loan_dashboard')




@login_required
def search_objects(request):
    query = request.GET.get('q', '')
    if query:
        objects = Object.objects.filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        ).filter(
            Q(loan__isnull=True) | Q(loan__return_date__isnull=True)
        ).distinct()
        results = [{'code': obj.code, 'name': obj.name} for obj in objects]
        return JsonResponse({'objects': results})
    return JsonResponse({'objects': []})

@login_required
def search_persons(request):
    query = request.GET.get('q', '')
    if query:
        persons = Person.objects.filter(RUT__icontains=query)[:10]
        results = [{'rut': person.RUT, 'name': f"{person.first_name} {person.last_name}".strip()} for person in persons]
        return JsonResponse({'persons': results})
    return JsonResponse({'persons': []})

@login_required
def objects_management(request):
    """Vista para la gestión de objetos"""
    kinds = Kind.objects.all()
    objects = Object.objects.all().order_by('-code')

    # Filtros de búsqueda
    query = request.GET.get('q', '').strip()
    kind_id = request.GET.get('kind', '').strip()
    if query:
        objects = objects.filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        )
    if kind_id:
        objects = objects.filter(kind_id=kind_id)

    objects = objects[:20]  # Últimos 20 objetos filtrados

    # Estadísticas adicionales
    total_objects = Object.objects.count()
    available_objects_count = Object.objects.filter(loan__return_date__isnull=False).distinct().count() + Object.objects.filter(loan__isnull=True).count()

    context = {
        'kinds': kinds,
        'objects': objects,
        'total_objects': total_objects,
        'available_objects_count': available_objects_count,
    }
    return render(request, 'objects/management.html', context)

@login_required
def create_objects_bulk(request):
    """Vista para crear objetos en lote"""
    if request.method == 'POST':
        try:
            kind_id = request.POST.get('kind')
            object_name = request.POST.get('object_name')
            quantity = int(request.POST.get('quantity', 1))
            start_number = int(request.POST.get('start_number', 1))

            if quantity > 100:
                messages.error(request, 'No se pueden crear más de 100 objetos a la vez')
                return redirect('objects_management')

            print(99)
            print(Kind.objects.all(), kind_id)
            kind = Kind.objects.get(code=kind_id)
            print(100)
            created_objects = []
            errors = []

            for i in range(quantity):
                current_number = start_number + i
                try:
                    obj = Object.objects.create(
                        name=object_name,
                        kind=kind,
                        number=current_number,
                        description=f'{object_name}'
                    )
                    created_objects.append(obj.code)
                except Exception as e:
                    errors.append(f'Error al crear objeto #{current_number}: {str(e)}')

            if created_objects:
                messages.success(request, f'Se crearon {len(created_objects)} objetos exitosamente')

            if errors:
                for error in errors[:5]:  # Mostrar solo los primeros 5 errores
                    messages.warning(request, error)

        except Kind.DoesNotExist:
            messages.error(request, 'Tipo de objeto no encontrado')
        except ValueError:
            messages.error(request, 'Cantidad o número inicial inválido')
        except Exception as e:
            messages.error(request, f'Error al crear objetos: {str(e)}')

    return redirect('objects_management')

@login_required
def create_kind(request):
    """Vista para crear un nuevo tipo de objeto"""
    if request.method == 'POST':
        try:
            code = request.POST.get('code').upper().strip()
            if not code or len(code) < 3:
                messages.error(request, 'El código debe tener al menos 3 caracteres')
                return redirect('objects_management')
            if Kind.objects.filter(code=code).exists():
                messages.error(request, f'El código "{code}" ya existe')
                return redirect('objects_management')
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')

            kind = Kind.objects.create(
                code=code,
                name=name,
                description=description
            )

            messages.success(request, f'Tipo de objeto "{code}" creado exitosamente')

        except Exception as e:
            messages.error(request, f'Error al crear tipo de objeto: {str(e)}')

    return redirect('objects_management')

@login_required
def persons_list(request):
    """Vista para la gestión de personas"""
    query = request.GET.get('q', '').strip()
    persons = Person.objects.all()
    if query:
        persons = persons.filter(
            Q(RUT__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    persons = persons.order_by('RUT')[:50]
    context = {
        'persons': persons,
        'query': query,
    }
    return render(request, 'persons/list.html', context)

@login_required
def edit_person(request, rut):
    person = get_object_or_404(Person, RUT=rut)
    if request.method == 'POST':
        person.first_name = request.POST.get('first_name', '')
        person.last_name = request.POST.get('last_name', '')
        person.email = request.POST.get('email', '')
        person.phone = request.POST.get('phone', '')
        person.comments = request.POST.get('comments', '')
        person.save()
        messages.success(request, 'Persona actualizada correctamente')
        return redirect('persons_list')
    return render(request, 'persons/edit.html', {'person': person})

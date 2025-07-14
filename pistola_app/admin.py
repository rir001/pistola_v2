from django.contrib import admin
from .models import Loan, Object, Person, Kind

# Register your models here.
@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'kind', 'number', 'description')
    list_filter = ('kind',)
    search_fields = ('name', 'kind__name', 'code')
    readonly_fields = ('code',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('RUT', 'first_name', 'last_name', 'email')
    search_fields = ('RUT', 'first_name', 'last_name', 'email')
    list_filter = ('first_name', 'last_name')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('object', 'person', 'loan_date', 'return_date')
    list_filter = ('loan_date', 'return_date')
    search_fields = ('object__name', 'person__first_name', 'person__last_name')
    raw_id_fields = ('object', 'person')

@admin.register(Kind)
class KindAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'name': ('description',)}
    ordering = ('name',)
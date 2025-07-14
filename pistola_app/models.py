from django.core.exceptions import ValidationError
from django.db import models

class Kind(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

def validate_code(value):
    if value > 9999:
        raise ValidationError(
            ("%(value)s is not less than or equal to 9999"),
            params={"value": value},
        )
    elif value < 0:
        raise ValidationError(
            ("%(value)s is not greater than or equal to 0"),
            params={"value": value},
        )

class Object(models.Model):
    name = models.CharField(max_length=100)

    kind = models.ForeignKey(Kind, on_delete=models.DO_NOTHING)
    number = models.IntegerField(unique=False, validators=[validate_code])

    code = models.CharField(max_length=7, primary_key=True, editable=False)

    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Generar el código automáticamente
        if not self.code:
            kind_code = self.kind.name[:3].upper()
            self.code = f"{kind_code}{self.number:04d}"
        super().save(*args, **kwargs)

    def is_loaned(self):
        """Retorna True si el objeto está actualmente prestado"""
        return self.loan_set.filter(return_date__isnull=True).exists()

    def __str__(self):
        return f"{self.code}"





class Person(models.Model):
    RUT = models.CharField(max_length=12, primary_key=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True, blank=True)

    def __str__(self):
        return f"{self.RUT}"




class Loan(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    loan_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.object.name} loaned to {self.person.RUT}"
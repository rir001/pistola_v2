from django.core.exceptions import ValidationError
from django.db import models
from datetime import date, timedelta
import numpy as np
import pandas as pd

class Kind(models.Model):
    code = models.CharField(max_length=3, primary_key=True, editable=False)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code




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

    def save(self, *args, **kwargs): # Executed before saving the object
        if not self.code:
            kind_code = self.kind.code[:3].upper()
            self.code = f"{kind_code}{self.number:04d}"
        super().save(*args, **kwargs)

    def is_loaned(self):
        """Retorna True si el objeto está actualmente prestado"""
        return self.loan_set.filter(return_date__isnull=True).exists()

    def __str__(self):
        return f"{self.code}"





class Person(models.Model):
    RUT         = models.CharField(max_length=9, primary_key=True)
    NA          = models.CharField(max_length=8, unique=True, blank=True, null=True)
    first_name  = models.CharField(max_length=50, blank=True)
    last_name   = models.CharField(max_length=50, blank=True)
    phone       = models.CharField(max_length=12, blank=True)
    email       = models.EmailField(unique=True, blank=True)
    comments    = models.TextField(blank=True)

    def __str__(self):
        return f"{self.RUT}"

    def get_debt(self):
        total_debt = 0
        for loan in self.loan_set.all():
            loan_date = loan.loan_date
            if loan.return_date:
                end_date = loan.return_date
            else:
                end_date = date.today()
            # Calcular días hábiles (lunes a viernes)
            days = np.busday_count(loan_date, end_date)
            overdue = max(0, days - 2)
            debt = min(overdue * 500, 6000)
            total_debt += debt
        return total_debt




class Loan(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    loan_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.object.name} loaned to {self.person.RUT}"
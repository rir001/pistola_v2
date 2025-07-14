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

    code = models.CharField(max_length=7, unique=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name





class Person(models.Model):
    RUT = models.CharField(max_length=12, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"




class Loan(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    loan_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.object.name} loaned to {self.person.first_name} {self.person.last_name}"
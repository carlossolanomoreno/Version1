# citas/validators.py

from django.core.exceptions import ValidationError

def validador_cedula(value):
    # Lógica para validar la cédula
    if not value.isdigit():
        raise ValidationError("La cédula debe ser un número.")
    if len(value) != 10:
        raise ValidationError("La cédula debe tener 10 dígitos.")


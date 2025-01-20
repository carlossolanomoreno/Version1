from django.db import models
from django.contrib.auth import get_user_model


# Obtener el modelo de usuario personalizado
Usuario = get_user_model()

class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return f"Administrador: {self.usuario.nombres} {self.usuario.apellidos}"
    
    
import random 
import string
import os
import requests
from django.contrib.auth.models import BaseUserManager, Group
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.apps import apps

class UsuarioManager(BaseUserManager):
    def create_user(self, cedula, correo_electronico, tipo_usuario, password=None, **extra_fields):
        """
        Crea y guarda un usuario con la cédula, correo electrónico y tipo de usuario proporcionados.
        """
        if not cedula:
            raise ValueError("La cédula es obligatoria")
        if not correo_electronico:
            raise ValueError("El correo electrónico es obligatorio")

        user = self.model(
            cedula=cedula,
            correo_electronico=correo_electronico,
            tipo_usuario=tipo_usuario,
            **extra_fields,
        )

        if not password:
            password = self.generate_random_password()
        
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError(f"Contraseña no válida: {', '.join(e.messages)}")
        
        user.set_password(password)

        # Asignar grupo para pacientes
        if tipo_usuario == 'Paciente':
            grupo_pacientes, created = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo_pacientes)

        # Asignar rol
        self.assign_role(user, tipo_usuario, extra_fields)

        # Guardar el usuario
        user.save(using=self._db)

        if user.chat_id:
            self.send_password_to_telegram(user.chat_id, password)

        return user

    def assign_role(self, user, tipo_usuario, extra_fields):
        """
        Asigna el rol correspondiente al usuario basado en el tipo de usuario.
        """
        try:
            RoleModel = apps.get_model('citas', tipo_usuario)
        except LookupError:
            raise ValueError(f"No se encontró un modelo asociado para el tipo de usuario '{tipo_usuario}'")

        role_instance = RoleModel.objects.create(usuario=user)

        # Crear instancia de Paciente si el tipo de usuario es Paciente
        if tipo_usuario == 'Paciente':
            Paciente.objects.create(usuario=user)

        if tipo_usuario == 'Medico' and 'especialidades' in extra_fields:
            role_instance.especialidades.set(extra_fields['especialidades'])
        elif tipo_usuario != 'Medico' and 'especialidades' in extra_fields:
            raise ValueError(f"El campo 'especialidades' no es válido para el tipo de usuario '{tipo_usuario}'")

    


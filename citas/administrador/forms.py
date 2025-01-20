from django import forms
from django.contrib.auth.models import User
from citas.models import Usuario, Paciente

class RegistroAdministradorForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['cedula', 'nombres', 'apellidos', 'username', 'correo_electronico', 'password', 'chat_id', 'telefono', 'direccion', 'ciudad_residencia', 'fecha_nacimiento', 'genero']

    # Personaliza los mensajes de error para el campo username
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'max_length': 'El nombre de usuario debe tener como máximo 150 caracteres.',
            'invalid': 'El nombre de usuario solo puede contener letras, números y los caracteres: @, ., +, -, _',
        }
    )

    def clean_correo_electronico(self):
        correo = self.cleaned_data.get('correo_electronico')
        if not correo:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        return correo



class RegistroPacienteForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'cedula', 'nombres', 'apellidos', 'correo_electronico', 'chat_id', 'telefono', 'direccion', 'ciudad_residencia', 'fecha_nacimiento', 'genero']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    



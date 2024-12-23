from django import forms
from .models import Usuario, Paciente, Cita, Diagnostico, RecetaMedica, ExamenMedico, Calificacion

# Codigo html
class RecuperarCredencialesForm(forms.Form):
    identificacion = forms.CharField(max_length=20, label="Identificación")
    correo = forms.EmailField(label="Correo Electrónico")

#Base de datos

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'cedula', 'apellidos', 'nombres', 'correo_electronico', 
            'telefono', 'direccion', 'ciudad_residencia', 
            'fecha_nacimiento', 'genero', 'username', 'password'
        ]
        widgets = {
            'password': forms.PasswordInput(),  # Campo de contraseña oculto
        }


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['usuario']
        

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['medico', 'especialidad', 'paciente', 'fecha_cita', 'hora_cita', 'estado']


class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['cita', 'descripcion']


class RecetaMedicaForm(forms.ModelForm):
    class Meta:
        model = RecetaMedica
        fields = ['cita', 'medicamentos', 'indicaciones']        
        

class ExamenMedicoForm(forms.ModelForm):
    class Meta:
        model = ExamenMedico
        fields = ['cita', 'tipo', 'descripcion']
        
        
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['cita', 'calificacion', 'comentario']
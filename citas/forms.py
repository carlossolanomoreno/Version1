from django import forms
from citas.models import Usuario, Administrador, Paciente, Cita, Diagnostico, Medico, Especialidad, RecetaMedica, ExamenMedico, Calificacion, HorarioMedico, Usuario, Secretaria, HistorialClinico
from django.core.exceptions import ValidationError
from .validators import validador_cedula
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password



# Codigo html
class RecuperarCredencialesForm(forms.Form):
    identificacion = forms.CharField(max_length=20, label="Identificación")
    correo = forms.EmailField(label="Correo Electrónico")

#Base de datos

def validador_cedula(value):
    if not value.isdigit() or len(value) != 10:
        raise ValidationError("La cédula debe contener 10 dígitos numéricos.")
    
def clean_telefono(self):
    telefono = self.cleaned_data.get('telefono')
    if telefono and not telefono.isdigit():
        raise forms.ValidationError("El número de teléfono solo debe contener dígitos.")
    return telefono

class RegistroUsuarioForm(forms.ModelForm):
    tipo_usuario = forms.ChoiceField(
        choices=Usuario.TIPO_USUARIO_CHOICES,
        required=True,
        widget=forms.Select
    )
    
    class Meta:
        model = Usuario
        fields = ['cedula', 'nombres', 'apellidos', 'correo_electronico', 'chat_id', 'telefono', 
                  'direccion', 'ciudad_residencia', 'fecha_nacimiento', 'username', 'genero', 'tipo_usuario', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario

    def clean_chat_id(self):
        chat_id = self.cleaned_data.get('chat_id')
        if not chat_id:
            raise forms.ValidationError("El chat_id es obligatorio para recibir notificaciones.")
        return chat_id

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("El campo 'username' no puede estar vacío.")
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso. Elige otro.")
        return username



class RegistroAdministradorForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'cedula', 'nombres', 'apellidos', 'username', 'correo_electronico', 
            'password', 'chat_id', 'telefono', 'direccion', 
            'ciudad_residencia', 'fecha_nacimiento', 'genero'
        ]

    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
            'max_length': 'El nombre de usuario debe tener como máximo 150 caracteres.',
            'invalid': 'El nombre de usuario solo puede contener letras, números y los caracteres: @, ., +, -, _',
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[validate_password],
        error_messages={'required': 'La contraseña es obligatoria.'}
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_correo_electronico(self):
        correo = self.cleaned_data.get('correo_electronico')
        if not correo:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        if Usuario.objects.filter(correo_electronico=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo




# Formulario de Registro de Paciente
class RegistroPacienteForm(forms.ModelForm):
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        label="Confirmar Contraseña",
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['cedula', 'username', 'nombres', 'apellidos', 'correo_electronico', 'chat_id', 'telefono', 
                  'direccion', 'ciudad_residencia', 'fecha_nacimiento', 'genero', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = 'Paciente'  # Asigna el tipo de usuario como 'Paciente'
        if commit:
            usuario.set_password(self.cleaned_data['password'])
            usuario.save()

            # Crear el grupo "Pacientes" si no existe
            grupo, creado = Group.objects.get_or_create(name='Pacientes')
            usuario.groups.add(grupo)  # Asocia el usuario al grupo "Pacientes"

            # Crear una entrada en la tabla Paciente
            paciente = Paciente.objects.create(usuario=usuario)

            print(f"Paciente {paciente.usuario.username} registrado correctamente.")

        return usuario

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_chat_id(self):
        chat_id = self.cleaned_data['chat_id']
        if Usuario.objects.filter(chat_id=chat_id).exists():
            raise ValidationError("El Chat ID ya está en uso.")
        return chat_id

def clean_cedula(self):
    cedula = self.cleaned_data.get('cedula')

    # Intentar convertir la cédula a un número entero
    try:
        cedula = int(cedula)
    except ValueError:
        raise forms.ValidationError('La cédula debe ser un número válido.')

    # Verificar que la cédula esté en el rango adecuado
    if cedula <= 0 or cedula > 9999999999:  # Ajusta el rango según tu país
        raise forms.ValidationError('La cédula debe ser un número positivo y no mayor a 9999999999.')

    return cedula
class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'

    
class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre_especialidad', 'descripcion_especialidad', 'estado']
        widgets = {
            'descripcion_especialidad': forms.Textarea(attrs={'rows': 3}),
            'estado': forms.Select(choices=Especialidad._meta.get_field('estado').choices),
        }

        
#Funciones del Paciente
class AgendarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'especialidad', 'medico', 'horario_medico']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # El administrador selecciona al paciente, por lo que el queryset debe incluir todos los pacientes.
        self.fields['paciente'].queryset = Paciente.objects.all()  # Todos los pacientes
        self.fields['especialidad'].queryset = Especialidad.objects.all()  # Todas las especialidades
        self.fields['medico'].queryset = Medico.objects.all()  # Todos los médicos
        self.fields['horario_medico'].queryset = HorarioMedico.objects.all()  # Todos los horarios

        # Opcional: Añadir etiquetas más descriptivas a los campos
        self.fields['paciente'].label = "Seleccione el paciente"
        self.fields['especialidad'].label = "Seleccione la especialidad"
        self.fields['medico'].label = "Seleccione el médico"
        self.fields['horario_medico'].label = "Seleccione el horario"






class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['especialidad', 'medico', 'horario_medico']

    def __init__(self, *args, **kwargs):
        # Obtén el usuario del argumento 'request' pasado al formulario
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Filtrar los horarios médicos
        self.fields['horario_medico'].queryset = HorarioMedico.objects.all()

    def save(self, commit=True):
        # Asigna automáticamente el paciente autenticado
        cita = super().save(commit=False)
        if self.request:
            cita.paciente = self.request.user.paciente
        if commit:
            cita.save()
        return cita
    
    

class CalificarCitaForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(attrs={'class': 'form-control'}),  # Menú desplegable
            'comentario': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


    
        
        
class HorarioMedicoForm(forms.ModelForm):
    class Meta:
        model = HorarioMedico
        fields = ['medico', 'dia', 'fecha', 'hora_inicio', 'hora_fin']

                   
        
class SecretariaForm(forms.ModelForm):
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        label="Confirmar Contraseña",
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['cedula', 'username', 'nombres', 'apellidos', 'correo_electronico', 'chat_id', 'telefono', 
                  'direccion', 'ciudad_residencia', 'fecha_nacimiento', 'genero', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = 'Secretaria'  # Asigna el tipo de usuario como 'Secretaria'
        if commit:
            # Encriptar la contraseña antes de guardarla
            usuario.set_password(self.cleaned_data['password'])
            
            # Guardar el usuario
            usuario.save()

            # Crear el grupo "Secretaria" si no existe
            grupo, creado = Group.objects.get_or_create(name='Secretarias')
            usuario.groups.add(grupo)  # Asocia el usuario al grupo "Secretaria"

            # Crear una entrada en la tabla Secretaria
            secretaria = Secretaria.objects.create(usuario=usuario)

            print(f"Secretaria {secretaria.usuario.username} registrada correctamente.")

        return usuario

    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_chat_id(self):
        chat_id = self.cleaned_data['chat_id']
        if Usuario.objects.filter(chat_id=chat_id).exists():
            raise ValidationError("El Chat ID ya está en uso.")
        return chat_id

def clean_cedula(self):
    cedula = self.cleaned_data.get('cedula')

    # Intentar convertir la cédula a un número entero
    try:
        cedula = int(cedula)
    except ValueError:
        raise forms.ValidationError('La cédula debe ser un número válido.')

    # Verificar que la cédula esté en el rango adecuado
    if cedula <= 0 or cedula > 9999999999:  # Ajusta el rango según tu país
        raise forms.ValidationError('La cédula debe ser un número positivo y no mayor a 9999999999.')

    return cedula

        
        

class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['cedula', 'username', 'nombres', 'apellidos', 'correo_electronico', 
                  'chat_id', 'telefono', 'direccion', 'ciudad_residencia', 
                  'fecha_nacimiento', 'genero', 'especialidad', 'password']
    
    # Especialidad solo se seleccionará después de registrar al médico
    especialidad = forms.ModelChoiceField(queryset=Especialidad.objects.all(), required=False, widget=forms.Select())

    class Meta:
        model = Usuario
        fields = [
            'cedula', 'username', 'nombres', 'apellidos', 'correo_electronico',
            'chat_id', 'telefono', 'direccion', 'ciudad_residencia',
            'fecha_nacimiento', 'genero', 'password'
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso.")
        return username

    def clean_chat_id(self):
        chat_id = self.cleaned_data.get('chat_id')
        if Usuario.objects.filter(chat_id=chat_id).exists():
            raise ValidationError("El Chat ID ya está en uso.")
        return chat_id

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit() or len(cedula) > 10:
            raise ValidationError("La cédula debe ser un número de máximo 10 dígitos.")
        return cedula
    
    
#Medico

class CambiarContrasenaForm(PasswordChangeForm):
    pass

class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['cita', 'medico', 'descripcion', 'fecha','proximo_control']

class RecetaForm(forms.ModelForm):
    class Meta:
        model = RecetaMedica
        fields = ['cita', 'medicamentos', 'indicaciones', 'medicamentos', 'fecha']

class ExamenForm(forms.ModelForm):
    class Meta:
        model = ExamenMedico
        fields = ['cita', 'tipo', 'descripcion']
        
    

class BuscarPacienteForm(forms.Form):
    cedula = forms.CharField(max_length=20, required=True, label='Número de Cédula')

    def buscar(self):
        cedula = self.cleaned_data.get('cedula')

        # Buscar al paciente por cédula
        queryset = Paciente.objects.filter(cedula=cedula)
        return queryset
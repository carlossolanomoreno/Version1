from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
import requests
import os
import random
import string
from citas.forms import (
    RegistroPacienteForm,
    AgendarCitaForm,
)
from citas.models import Secretaria, Paciente, Usuario, Especialidad, Medico, HorarioMedico
from django.contrib.auth.views import PasswordChangeView
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)
from django.contrib.auth import logout

# Recuperación de credenciales
# Función para generar contraseñas seguras
def generate_random_password(length=12):
    if length < 8:
        raise ValueError("La longitud mínima de la contraseña debe ser de 8 caracteres.")
    
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_+=<>?"
    password = ''.join(random.choices(characters, k=length))
    return password

def logout_secretaria(request):
    logout(request)
    return redirect('secretaria:login_secretaria')

def login_secretaria(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')

        # Validar que los campos no estén vacíos
        if not cedula or not password:
            messages.error(request, "Por favor, ingresa la cédula y la contraseña.")
            return redirect('secretaria:login_secretaria')

        # Buscar el usuario por cédula
        try:
            usuario = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('secretaria:login_secretaria')

        # Verificar contraseña y tipo de usuario
        if usuario.check_password(password) and usuario.tipo_usuario == 'Secretaria':
            login(request, usuario)  # Autenticar al usuario
            return redirect('secretaria:dashboard_secretaria')  # Redirige al dashboard
        else:
            messages.error(request, "Credenciales incorrectas o no tienes autorización.")
            return redirect('secretaria:login_secretaria')

    return render(request, 'secretaria/login_secretaria.html')



# Enviar mensaje a Telegram
def enviar_mensaje_telegram(chat_id, mensaje, token):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': mensaje
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje a Telegram: {e}")
        return False

# Recuperación de credenciales
def recuperar_credenciales_secretaria(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        if not cedula:
            return JsonResponse({'error': 'Debes proporcionar una cédula.'}, status=400)

        try:
            usuario = Usuario.objects.get(cedula=cedula)

            if not usuario.chat_id or usuario.chat_id.strip() == "":
                return JsonResponse({
                    'error': 'El usuario no tiene un chat_id asociado. Contacta al administrador del sistema.'
                }, status=404)

            nueva_password = generate_random_password()
            usuario.set_password(nueva_password)
            usuario.save()

            mensaje = (
                f"Hola {usuario.nombres},\n"
                f"Tu nueva contraseña temporal es: {nueva_password}\n"
                f"Por favor, cámbiala después de iniciar sesión."
            )
            token_telegram = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token_telegram:
                return JsonResponse({
                    'error': 'El sistema no tiene configurado un token de Telegram. Contacta al administrador.'
                }, status=500)

            if enviar_mensaje_telegram(usuario.chat_id, mensaje, token_telegram):
                return JsonResponse({'mensaje': 'Se ha enviado una nueva contraseña a tu Telegram.'})
            else:
                return JsonResponse({'error': 'No se pudo enviar el mensaje a través de Telegram.'}, status=500)

        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Credenciales incorrectas.'}, status=404)

        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

    return render(request, 'secretaria/recuperar_credenciales_secretaria.html')


# Verifica si un usuario pertenece a un grupo específico
def verificar_grupo(usuario, grupo_nombre):
    return usuario.groups.filter(name=grupo_nombre).exists()


# Vista del dashboard de secretaria

@login_required
def dashboard_secretaria(request):
    """
    Dashboard de la secretaria para registrar pacientes, agendar citas y ver su perfil.
    """
    # Verifica que el usuario pertenece al grupo "Secretaria"
    if request.user.tipo_usuario != 'Secretaria':
        messages.error(request, "Acceso denegado.")
        return redirect('login_secretaria')

    # Obtener información básica de la secretaria
    try:
        secretaria = Secretaria.objects.get(usuario=request.user)
    except Secretaria.DoesNotExist:
        messages.error(request, "No se encuentra el perfil asociado.")
        return redirect('login_secretaria')

    # Manejo del formulario para registrar pacientes
    if request.method == "POST" and "registrar_paciente" in request.POST:
        paciente_form = RegistroPacienteForm(request.POST)
        if paciente_form.is_valid():
            paciente_form.save()
            messages.success(request, "Paciente registrado exitosamente.")
            return redirect('dashboard_secretaria')
        else:
            messages.error(request, "Error al registrar al paciente. Verifica los datos.")
    else:
        paciente_form = RegistroPacienteForm()

    # Manejo del formulario para agendar citas médicas
    if request.method == "POST" and "agendar_cita" in request.POST:
        cita_form = AgendarCitaForm(request.POST)
        if cita_form.is_valid():
            cita_form.save()
            messages.success(request, "Cita médica agendada exitosamente.")
            return redirect('dashboard_secretaria')
        else:
            messages.error(request, "Error al agendar la cita médica. Verifica los datos.")
    else:
        cita_form = AgendarCitaForm()

    # Enlace al perfil de la secretaria (usando el namespace correcto)
    url_perfil_secretaria = reverse('secretaria:perfil_secretaria', args=[secretaria.id])

    return render(request, 'secretaria/dashboard_secretaria.html', {
        'secretaria': secretaria,
        'paciente_form': paciente_form,
        'cita_form': cita_form,
        'url_perfil_secretaria': url_perfil_secretaria,
    })


def perfil_secretaria(request, id):
    # Lógica para obtener los datos de la secretaria usando 'id'
    secretaria = get_object_or_404(Secretaria, usuario__id=id)  # Ajusta esto según tu modelo
    return render(request, 'secretaria/perfil_secretaria.html', {'secretaria': secretaria})


class CambiarContrasenaView(PasswordChangeView):
    template_name = 'secretaria/cambiar_contrasena.html'
    success_url = reverse_lazy('secretaria:dashboard_secretaria')

    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña se ha cambiado correctamente.')
        return super().form_valid(form)



# Vista para agendar citas


def registrar_paciente_secre(request):
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            # Asignar grupo 'Pacientes'
            pacientes_group, _ = Group.objects.get_or_create(name='Pacientes')
            usuario.groups.add(pacientes_group)

            Paciente.objects.create(usuario=usuario)

            messages.success(request, "Paciente registrado exitosamente.")
            return redirect('secretaria_dashboard')  # Redirige al dashboard de secretaria
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = RegistroPacienteForm()

    return render(request, 'secretaria/registrar_paciente_secre.html', {'form': form})

@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            # Se asocia el paciente seleccionado
            cita.paciente = form.cleaned_data['paciente']
            cita.save()
            return redirect('cita_agendada')  # Redirigir a una página que confirme que la cita fue agendada
    else:
        form = AgendarCitaForm()

    return render(request, 'secretaria/agendar_cita.html', {'form': form})



def cargar_medicos(request):
    especialidad_id = request.GET.get('especialidad_id')
    try:
        especialidad = Especialidad.objects.get(id=especialidad_id)
        medicos = Medico.objects.filter(especialidades=especialidad)
        medico_data = [{'id': medico.id, 'nombre': f"{medico.usuario.nombres} {medico.usuario.apellidos}"} for medico in medicos]
        return JsonResponse({'medicos': medico_data})
    except Especialidad.DoesNotExist:
        return JsonResponse({'error': 'Especialidad no encontrada'}, status=400)

def cargar_horarios(request):
    medico_id = request.GET.get('medico_id')
    try:
        # Busca el médico correspondiente
        medico = Usuario.objects.get(id=medico_id, tipo_usuario='Médico')

        # Filtra horarios solo por el médico y los tres meses
        hoy = timezone.now()
        # Establecer el primer día del mes actual
        fecha_inicio = hoy.replace(day=1)  # Primer día del mes actual
        # Establecer el primer día del cuarto mes
        fecha_fin = (fecha_inicio.replace(month=fecha_inicio.month + 3) 
             if fecha_inicio.month <= 9 
             else fecha_inicio.replace(year=fecha_inicio.year + 1, month=(fecha_inicio.month + 3 - 12)))


        # Filtra los horarios para los tres meses
        horarios = HorarioMedico.objects.filter(
            medico=medico,
            fecha__gte=fecha_inicio,
            fecha__lt=fecha_fin
        )

        # Genera los datos de respuesta, incluyendo la fecha y el mes
        horario_data = [
            {
                'id': horario.id,
                'dia': horario.dia,
                'fecha': horario.fecha.strftime('%d/%m/%Y'),  # Fecha completa (día/mes/año)
                'mes': horario.fecha.strftime('%B'),  # Nombre del mes (por ejemplo, "Enero")
                'ano': horario.fecha.strftime('%Y'),  # Año
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
            }
            for horario in horarios
        ]

        return JsonResponse({'horarios': horario_data})

    except Medico.DoesNotExist:
        return JsonResponse({'error': 'Médico no encontrado'}, status=400)


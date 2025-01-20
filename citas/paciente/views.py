from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
import requests
import os
import random
import string

from citas.forms import (
    RegistroPacienteForm,
    CalificarCitaForm,
    PacienteForm,
    CitaForm,
)
from citas.models import Paciente, Cita, Usuario, Especialidad, Medico, HorarioMedico
from django.contrib.auth.views import PasswordChangeView
from .forms import FotoPerfilForm  # Formulario para subir foto de perfil


# Función para generar contraseñas aleatorias
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Verifica si un usuario pertenece a un grupo específico
def verificar_grupo(usuario, grupo_nombre):
    return usuario.groups.filter(name=grupo_nombre).exists()


# Vista de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')

        if not cedula or not password:
            messages.error(request, "Por favor, ingresa la cédula y la contraseña.")
            return redirect('login_paciente')

        try:
            user = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('login_paciente')

        if user.check_password(password):
            login(request, user)
            if user.tipo_usuario == 'Paciente':
                return redirect('dashboard_paciente')
            else:
                return redirect('home')
        else:
            messages.error(request, "Credenciales incorrectas.")
            return redirect('login_paciente')

    return render(request, 'paciente/login_paciente.html')


# Vista para registrar pacientes
def registro_paciente(request):
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

            messages.success(request, "Usuario registrado y paciente creado exitosamente.")
            return redirect('login_paciente')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = RegistroPacienteForm()

    return render(request, 'paciente/registro_paciente.html', {'form': form})



# Recuperación de credenciales
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

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

def recuperar_credenciales(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        if not cedula:
            return JsonResponse({'error': 'Debes proporcionar una cédula.'}, status=400)

        try:
            usuario = Usuario.objects.get(cedula=cedula)

            if not usuario.chat_id or usuario.chat_id.strip() == "":
                return JsonResponse({'error': 'El usuario no tiene un chat_id asociado.'}, status=404)

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
                return JsonResponse({'error': 'Token de Telegram no configurado.'}, status=500)

            if enviar_mensaje_telegram(usuario.chat_id, mensaje, token_telegram):
                return JsonResponse({'mensaje': 'Se ha enviado una nueva contraseña a tu Telegram.'})
            else:
                return JsonResponse({'error': 'No se pudo enviar el mensaje a través de Telegram.'}, status=500)

        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'La cédula no está registrada.'}, status=404)

        except Exception as e:
            return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

    return render(request, 'paciente/recuperar_credenciales_paciente.html')

# Vista del dashboard del paciente
@login_required
def dashboard_paciente(request):
    if not verificar_grupo(request.user, 'Pacientes'):
        messages.error(request, "Acceso denegado.")
        return redirect('login_paciente')

    try:
        paciente = Paciente.objects.get(usuario=request.user)
    except Paciente.DoesNotExist:
        messages.error(request, "No se encuentra el paciente asociado.")
        return redirect('login_paciente')

    # Obtener citas pendientes
    citas_pendientes = Cita.objects.filter(paciente=paciente, estado='pendiente')  # Ajusta el filtro según tu modelo

    if not citas_pendientes.exists():
        messages.info(request, "No tienes citas para calificar.")

    url_agendar_cita = reverse('agendar_cita')
    return render(request, 'paciente/dashboard_paciente.html', {
        'paciente': paciente,
        'url_agendar_cita': url_agendar_cita,
        'citas_pendientes': citas_pendientes  # Pasamos las citas al contexto
    })


# Vista para ver el perfil del paciente
@login_required
def perfil_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, usuario=request.user)

    if request.method == 'POST':
        form = FotoPerfilForm(request.POST, request.FILES, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu foto de perfil se ha actualizado correctamente.')
            return redirect('perfil_paciente', paciente_id=paciente.id)
    else:
        form = FotoPerfilForm(instance=paciente)

    return render(request, 'paciente/perfil_paciente.html', {'paciente': paciente, 'form': form})

# Vista para cambiar contraseña
class CambiarContrasenaView(PasswordChangeView):
    template_name = 'paciente/cambiar_contrasena.html'
    success_url = reverse_lazy('dashboard_paciente')

    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña se ha cambiado correctamente.')
        return super().form_valid(form)

#Actualizar foto de perfil
def actualizar_foto_perfil(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = FotoPerfilForm(request.POST, request.FILES, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('nombre_de_la_url')  # Redirigir a la página deseada
    else:
        form = FotoPerfilForm(instance=paciente)
    return render(request, 'citas/paciente/actualizar_foto.html', {'form': form})



# Vista para agendar citas

def agendar_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cita_agendada')  # Redirigir a una página de confirmación
    else:
        form = CitaForm()

    return render(request, 'paciente/agendar_cita.html', {'form': form})

def cita_agendada(request):
    cita = Cita.objects.filter(paciente=request.user.paciente).last() 
    return render(request, 'paciente/cita_agendada.html', {'cita': cita})


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
        medico = Medico.objects.get(id=medico_id)

        # Filtra horarios solo por el médico (sin el campo `estado`)
        horarios = HorarioMedico.objects.filter(medico=medico)

        # Genera los datos de respuesta
        horario_data = [
            {
                'id': horario.id,
                'dia': horario.dia,
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
            }
            for horario in horarios
        ]

        return JsonResponse({'horarios': horario_data})
    except Medico.DoesNotExist:
        return JsonResponse({'error': 'Médico no encontrado'}, status=400)
    




# Vista para calificar citas
@login_required
def calificar_cita(request, cita_id):
    try:
        paciente = Paciente.objects.get(usuario=request.user)
    except Paciente.DoesNotExist:
        messages.error(request, "No se encontró el paciente asociado.")
        return redirect('listar_citas')

    cita = get_object_or_404(Cita, id=cita_id, paciente=paciente)
    if request.method == 'POST':
        form = CalificarCitaForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.cita = cita
            calificacion.save()
            messages.success(request, "Calificación registrada exitosamente.")
            return redirect('listar_citas')
    else:
        form = CalificarCitaForm()

    return render(request, 'paciente/calificar_cita.html', {'form': form, 'cita': cita})


# Vista para actualizar información del paciente
@login_required
def actualizar_informacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Información actualizada exitosamente.")
            return redirect('perfil_paciente', paciente_id=paciente.id)
    else:
        form = PacienteForm(instance=paciente)

    return render(request, 'paciente/actualizar_informacion.html', {'form': form})








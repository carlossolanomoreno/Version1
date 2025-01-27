from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg
from citas.forms import ( CambiarContrasenaForm, DiagnosticoForm, RecetaForm, ExamenForm, BuscarPacienteForm)
from citas.models import (
    Paciente, Medico, Cita, HistorialClinico, Diagnostico, RecetaMedica, ExamenMedico, Usuario
)
import requests
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import PermissionDenied

def home(request):
    return render(request, 'index.html')

# Formulario de inicio de sesión

def login_medico(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')

        if not cedula or not password:
            messages.error(request, "Por favor, ingresa la cédula y la contraseña.")
            return redirect('login_medico')

        try:
            user = Usuario.objects.get(cedula=cedula)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return redirect('login_medico')

        if user.check_password(password):
            login(request, user)
            if user.tipo_usuario == 'Medico':
                return redirect('dashboard_medico')
            else:
                return redirect('login_medico')
        else:
            messages.error(request, "Credenciales incorrectas.")
            return redirect('login_medico')

    return render(request, 'medico/login_medico.html')

@login_required
def dashboard_medico(request):
    pacientes = None  # Inicializamos la variable pacientes
    if request.method == 'POST':
        form = BuscarPacienteForm(request.POST)
        if form.is_valid():
            pacientes = form.buscar()  # Realizamos la búsqueda en la base de datos
            if pacientes.exists():
                return render(request, 'medico/dashboard_medico.html', {'form': form, 'pacientes': pacientes})
            else:
                messages.error(request, "No se encontraron pacientes con ese nombre, apellido o cédula.")
        else:
            messages.error(request, "Por favor ingresa un término de búsqueda válido.")
    else:
        form = BuscarPacienteForm()

    # Renderizamos la plantilla con la variable pacientes (puede ser None si no se encuentra nada)
    return render(request, 'medico/dashboard_medico.html', {'form': form, 'pacientes': pacientes})


@login_required
def perfil_medico(request):
    if request.method == "POST":
        form = SetPasswordForm(user=request.user, data=request.POST)  # Pasa `user` explícitamente
        if form.is_valid():
            form.save()
            messages.success(request, "Tu contraseña se ha cambiado correctamente.")
            return redirect("citas:dashboard_medico")
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = SetPasswordForm(user=request.user)  # Pasa `user` explícitamente

    return render(request, "medico/perfil_medico.html", {"form": form})

@login_required
def agenda_medico(request):
    # Verificar que el usuario autenticado tenga el perfil de médico
    if not hasattr(request.user, 'medico'):
        raise PermissionDenied("Solo los médicos pueden acceder a esta página.")  # Más específico que redirigir al home

    # Obtener el perfil del médico asociado al usuario autenticado
    medico = request.user.medico  

    # Filtrar las citas asociadas al médico y ordenarlas por día y hora
    citas = Cita.objects.filter(medico=medico).order_by('horario_medico__dia', 'horario_medico__hora_inicio')

    # Debugging: Imprimir las citas y el paciente asociado
    for cita in citas:
        if cita.paciente:
            print(f"Paciente: {cita.paciente.usuario.nombres} {cita.paciente.usuario.apellidos}")
        else:
            print("Cita sin paciente asociado")

    # Renderizar la plantilla con las citas en el contexto
    return render(request, 'medico/agenda_medico.html', {'citas': citas})



@login_required 
def actualizar_estado_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, medico=request.user.medico)  # Asegurarse de que el médico sea el dueño de la cita

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')  # El nuevo estado se recibe desde un formulario
        
        # Validación de cambios de estado (evitar transiciones no lógicas)
        if nuevo_estado == 'Pendiente' and cita.estado in ['Finalizada', 'Cancelada']:
            messages.error(request, "No puedes cambiar una cita finalizada o cancelada a pendiente.")
        elif nuevo_estado == 'Finalizada' and cita.estado != 'Pendiente':
            messages.error(request, "Solo puedes finalizar una cita que esté pendiente.")
        elif nuevo_estado == 'Cancelada' and cita.estado == 'Finalizada':
            messages.error(request, "No puedes cancelar una cita que ya está finalizada.")
        else:
            # Actualizar estado de la cita
            if nuevo_estado in ['Pendiente', 'Finalizada', 'Cancelada']:
                cita.estado = nuevo_estado
                cita.save()
                messages.success(request, f"Estado de la cita actualizado a {nuevo_estado}.")
            else:
                messages.error(request, "Estado inválido.")
        
        return redirect('agenda_medico')  # Asegúrate de que esta vista exista y muestre las citas correctamente.




@login_required
def generar_diagnostico(request):
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diagnóstico generado correctamente.')
            return redirect('dashboard_medico')
    else:
        form = DiagnosticoForm()
    return render(request, 'medico/generar_diagnostico.html', {'form': form})


@login_required
def generar_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receta generada correctamente.')
            return redirect('dashboard_medico')
    else:
        form = RecetaForm()
    return render(request, 'medico/generar_receta.html', {'form': form})

@login_required
def solicitar_examen(request):
    if request.method == 'POST':
        form = ExamenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examen solicitado correctamente.')
            return redirect('dashboard_medico')
    else:
        form = ExamenForm()
    return render(request, 'medico/solicitar_examen.html', {'form': form})


def ver_historial(request, paciente_id):
    print(f"Paciente ID: {paciente_id}")
    paciente = get_object_or_404(Paciente, id=paciente_id)
    historial = HistorialClinico.objects.filter(paciente=paciente)
    return render(request, 'medico/ver_historial.html', {'paciente': paciente, 'historial': historial})




from django.db import transaction

def crear_historial_clinico(paciente, diagnosticos=None, examenes=None, recetas=None):
    """
    Crea o actualiza un historial clínico para el paciente dado.
    """
    with transaction.atomic():
        historial, created = HistorialClinico.objects.get_or_create(paciente=paciente)

        # Agrega los diagnósticos
        if diagnosticos:
            historial.diagnosticos.add(*diagnosticos)

        # Agrega los exámenes médicos
        if examenes:
            historial.examenes.add(*examenes)

        # Agrega las recetas médicas
        if recetas:
            historial.recetas.add(*recetas)

        historial.save()
        return historial





def buscar_paciente(request):
    paciente = None
    historial = None

    if 'cedula' in request.GET:
        cedula = request.GET['cedula']
        paciente = Paciente.objects.filter(usuario__cedula=cedula).first()

        if paciente:
            # Recuperar el historial con las relaciones de muchos a muchos
            historial = HistorialClinico.objects.filter(paciente=paciente).prefetch_related(
                'diagnosticos', 'examenes', 'recetas'
            ).first()

    return render(request, 'medico/dashboard_medico.html', {'paciente': paciente, 'historial': historial})


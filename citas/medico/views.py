from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.db.models import Avg
from citas.forms import ( CambiarContrasenaForm, DiagnosticoForm, RecetaForm, ExamenForm)
from citas.models import (
    Paciente, Medico, Cita, HistorialClinico, Diagnostico, RecetaMedica, ExamenMedico, Usuario, Agenda
)
import requests
from django.contrib.auth.forms import SetPasswordForm

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
    return render(request, 'medico/dashboard_medico.html')

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
def ver_agenda(request):
    # Obtener el médico autenticado
    medico = request.user.medico
    
    # Buscar la agenda asociada al médico
    agenda = get_object_or_404(Agenda, medico=medico)

    # Obtener las citas pendientes
    citas_pendientes = agenda.citas_pendientes()

    return render(request, "medico/ver_agenda.html", {"citas_pendientes": citas_pendientes})

@login_required
def ver_historial_clinico(request):
    cedula = request.GET.get('cedula')
    historial = None
    if cedula:
        try:
            historial = HistorialClinico.objects.filter(paciente__usuario__cedula=cedula)
        except HistorialClinico.DoesNotExist:
            messages.error(request, "No se encontró el historial clínico.")
    return render(request, 'medico/ver_historial_clinico.html', {'historial': historial})

@login_required
def generar_diagnostico(request):
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diagnóstico generado correctamente.')
            return redirect('citas:dashboard_medico')
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
            return redirect('citas:dashboard_medico')
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
            return redirect('citas:dashboard_medico')
    else:
        form = ExamenForm()
    return render(request, 'medico/solicitar_examen.html', {'form': form})
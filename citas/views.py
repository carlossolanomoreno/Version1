from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from citas.forms import (
    RegistroUsuarioForm
)
from citas.models import Usuario
import requests
import logging
from django.contrib.auth import login

logger = logging.getLogger(__name__)  # Configura logging para depuración

# Vista de inicio
def home(request):
    return render(request, 'index.html')

# Registro de usuario
def registrar_usuario(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            # Asignar al grupo 'Pacientes'
            grupo_pacientes = Group.objects.get(name='Pacientes')
            usuario.groups.add(grupo_pacientes)

            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('login')
        else:
            messages.error(request, "Hubo un error en el registro.")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registro_usuario.html', {'form': form})

# Función para enviar notificaciones por Telegram
def enviar_notificacion(usuario_id, mensaje):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Verificar si el usuario tiene un chat_id asociado
    if not usuario.chat_id:
        return JsonResponse({'error': 'El usuario no tiene un chat_id asociado.'}, status=404)

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': usuario.chat_id,
        'text': mensaje
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return JsonResponse({'success': 'Notificación enviada exitosamente.'}, status=200)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al enviar notificación: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    

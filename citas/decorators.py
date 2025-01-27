from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from functools import wraps
from citas.models import Administrador, Paciente, Medico, Secretaria
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def role_required(role, response_format="html"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Por favor, inicia sesión para continuar.")
                return redirect('login_secretaria')  # Redirige al login de secretaria si no está autenticado

            # Mapear roles a modelos
            role_mapping = {
                "Paciente": Paciente,
                "Administrador": Administrador,
                "Medico": Medico,
                "Secretaria": Secretaria,
            }

            if role not in role_mapping:
                messages.error(request, "Rol no válido.")
                return redirect('login_secretaria')

            role_model = role_mapping[role]
            if not role_model.objects.filter(usuario=request.user).exists():
                messages.error(request, f"No tienes permiso para acceder a esta vista. Rol requerido: {role}")
                return redirect('login_secretaria')

            role_instance = get_object_or_404(role_model, usuario=request.user)
            kwargs[role.lower()] = role_instance
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator



def administrador_required(view_func):
    """
    Decorador que asegura que el usuario autenticado es un administrador.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Verifica si el usuario está autenticado y si es administrador
        if not request.user.is_authenticated or request.user.tipo_usuario != 'Administrador':
            return redirect('login_admin')  # Redirige a la página de inicio de sesión si no cumple
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def secretaria_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name="Secretarias").exists() or request.user.tipo_usuario != 'Secretaria':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('login_secretaria')  # Redirige al login de secretarias si no es secretaria
        return view_func(request, *args, **kwargs)
    return _wrapped_view

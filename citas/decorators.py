from functools import wraps
from django.http import JsonResponse
from citas.models import Paciente, Administrador, Medico, Secretaria
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({"error": "Autenticación requerida"}, status=401)

            role_mapping = {
                "Paciente": Paciente,
                "Administrador": Administrador,
                "Medico": Medico,
                "Secretaria": Secretaria,
            }

            if role not in role_mapping:
                return JsonResponse({"error": "Rol no válido"}, status=400)

            role_model = role_mapping[role]
            if not role_model.objects.filter(usuario=user).exists():
                return JsonResponse(
                    {"error": f"Permiso denegado. Se requiere el rol: {role}"},
                    status=403,
                )

            role_instance = get_object_or_404(role_model, usuario=user)
            kwargs[role.lower()] = role_instance

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator

def administrador_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Verifica que el usuario esté autenticado y sea un administrador
        if not request.user.is_authenticated or request.user.tipo_usuario != 'Administrador':
            return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
        # Llama a la vista original con los argumentos originales
        return view_func(request, *args, **kwargs)
    return _wrapped_view


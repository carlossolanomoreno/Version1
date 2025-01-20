from rest_framework.permissions import BasePermission

class IsSecretaria(BasePermission):
    """
    Permiso personalizado para verificar si el usuario autenticado
    tiene un perfil de 'Secretaria'.
    """
    def has_permission(self, request, view):
        # Verifica si el usuario autenticado tiene un atributo 'secretaria'
        return hasattr(request.user, 'secretaria')

class IsAdministrador(BasePermission):
    """
    Permiso personalizado para verificar si el usuario autenticado
    tiene un perfil de 'Administrador'.
    """
    def has_permission(self, request, view):
        # Verifica si el usuario tiene el atributo 'tipo_usuario' y si es 'Administrador'
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'tipo_usuario') and 
            request.user.tipo_usuario == 'Administrador'
        )

    


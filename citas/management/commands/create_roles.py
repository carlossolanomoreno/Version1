from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from citas.models import Paciente, Administrador, Medico, Secretaria  # Importar modelos específicos

def create_roles():
    """
    Crea roles predefinidos (Grupos) en el sistema y asigna los permisos correspondientes.
    """
    # Diccionario de roles y sus permisos
    roles_permisos = {
        'Paciente': [
            'add_cita',  # Permitir que los pacientes agenden citas
            'change_cita',  # Modificar citas propias
            'view_cita',  # Ver sus citas
            'add_calificacion',  # Calificar citas
            'view_historial_clinico',  # Ver historial clínico propio
        ],
        'Administrador': [
            'add_user',  # Crear usuarios
            'change_user',  # Modificar usuarios
            'delete_user',  # Eliminar usuarios
            'view_user',  # Ver usuarios
            'add_horariomedico',  # Crear horarios médicos
            'change_horariomedico',  # Modificar horarios médicos
            'delete_horariomedico',  # Eliminar horarios médicos
            'view_horariomedico',  # Ver horarios médicos
            'add_reporteestadistico',  # Generar reportes estadísticos
        ],
        'Médico': [
            'add_diagnostico',  # Generar diagnósticos
            'view_diagnostico',  # Ver diagnósticos
            'add_recetamedica',  # Generar recetas médicas
            'view_recetamedica',  # Ver recetas médicas
            'add_examenmedico',  # Solicitar exámenes médicos
            'view_examenmedico',  # Ver exámenes médicos
            'view_historial_clinico',  # Ver historial clínico de pacientes
            'add_horariomedico',  # Registrar horarios de atención
            'view_cita',  # Ver citas propias
        ],
        'Secretaria': [
            'add_cita',  # Agendar citas
            'change_cita',  # Modificar citas
            'delete_cita',  # Cancelar citas
            'view_cita',  # Ver citas
            'view_user',  # Ver información de usuarios
        ],
    }

    # Crear roles y asignar permisos
    for role, permisos in roles_permisos.items():
        # Crear o recuperar el grupo
        grupo, created = Group.objects.get_or_create(name=role)
        print(f"Grupo {'creado' if created else 'existente'}: {role}")

        # Asignar permisos al grupo
        for permiso_codename in permisos:
            try:
                permiso = Permission.objects.get(codename=permiso_codename)
                grupo.permissions.add(permiso)
                print(f"Permiso asignado a {role}: {permiso_codename}")
            except Permission.DoesNotExist:
                print(f"Permiso no encontrado: {permiso_codename}")
            except Exception as e:
                print(f"Error al asignar el permiso {permiso_codename} a {role}: {e}")



from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import login_view

urlpatterns = [
    # Ruta para el login de pacientes
    path('login', login_view, name='login_paciente'),
    

    # Registro de pacientes
    path('registro/', views.registro_paciente, name='registro_paciente'),

    # Dashboard del paciente
    path('dashboard-paciente/', views.dashboard_paciente, name='dashboard_paciente'),

    # Actualización de información del paciente
    path('actualizar/<int:paciente_id>/', views.actualizar_informacion, name='actualizar_informacion'),

    # Agendar citas
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('cargar_medicos/', views.cargar_medicos, name='cargar_medicos'),
    path('cita_agendada/', views.cita_agendada, name='cita_agendada'),

    # Calificar citas
    path('calificar/<int:cita_id>/', views.calificar_cita, name='calificar_cita'),

    # Perfil del paciente
    path('perfil/<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente'),

    # Actualización de la foto de perfil
    path('perfil/<int:paciente_id>/actualizar-foto/', views.actualizar_foto_perfil, name='actualizar_foto_perfil'),

    # Recuperar credenciales
    path('recuperar-credenciales/', views.recuperar_credenciales, name='recuperar_credenciales_paciente'),

    # Cambiar contraseña
    path('cambiar-contrasena/', views.CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
]


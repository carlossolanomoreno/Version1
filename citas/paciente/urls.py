from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import login_view, cargar_horarios

urlpatterns = [
    # Ruta para el login de pacientes
    path('login', login_view, name='login_paciente'),
    
    # Registro de pacientes
    path('registro/', views.registro_paciente, name='registro_paciente'),

    # Dashboard del paciente
    path('dashboard-paciente/', views.dashboard_paciente, name='dashboard_paciente'),

    # Agendar citas
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('cargar_medicos/', views.cargar_medicos, name='cargar_medicos'),
    path('cita_agendada/', views.cita_agendada, name='cita_agendada'),
    path('cargar-horarios/', cargar_horarios, name='cargar_horarios'),
    
    # Calificar citas
    path('calificar/<int:cita_id>/', views.calificar_cita, name='calificar_cita'),

    # Perfil del paciente
    path('perfil/<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente'),
    #  Cambiar contraseña
    path('cambiar-contrasena/', views.CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
  
    # Recuperar credenciales
    path('recuperar-credenciales/', views.recuperar_credenciales, name='recuperar_credenciales_paciente'),

    # Cambiar contraseña
    path('cambiar-contrasena/', views.CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
]


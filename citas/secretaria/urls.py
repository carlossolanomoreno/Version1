from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import cargar_horarios

app_name = 'secretaria'

urlpatterns = [
    
    path('login/', views.login_secretaria, name='login_secretaria'),
    path('logout/', views.logout_secretaria, name='logout_secretaria'),
    # Registro de pacientes
    path('registrar_paciente/', views.registrar_paciente_secre, name='registrar_paciente_secre'),

    # Dashboard del paciente
    path('dashboard/', views.dashboard_secretaria, name='dashboard_secretaria'),
    
    # Agendar citas
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('cargar_medicos/', views.cargar_medicos, name='cargar_medicos'),
    path('cargar-horarios/', cargar_horarios, name='cargar_horarios'),
    

    # Recuperar credenciales
    path('recuperar-credenciales/', views.recuperar_credenciales_secretaria, name='recuperar_credenciales_secretaria'),

    # Cambiar contraseña
    path('cambiar-contrasena/', views.CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
    path('perfil/<int:id>/', views.perfil_secretaria, name='perfil_secretaria'),
]

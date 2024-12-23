"""
URL configuration for citas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from .views import login_view
from django.contrib import admin

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    path('', views.home, name='home'),
    
    path('home/', views.home, name='home'),
    
    path('login/', login_view, name='login'),
    
    
    
    path('recuperar-credenciales/', views.recuperar_credenciales, name='recuperar_credenciales'),
    
    # Ruta para registrar un usuario
    path('usuario_registro/', views.registrar_usuario, name='registrar_usuario'),
    
    path('listar_usuarios/', views.listar_usuarios, name='listar_usuarios'),
    
    # Ruta para registrar un paciente
    path('pacientes/registro/', views.registrar_paciente, name='registrar_paciente'),
    
    # Ruta para agendar una cita
    path('citas/agendar/', views.agendar_cita, name='agendar_cita'),
    
    # Ruta para listar citas
    path('citas/lista/', views.listar_citas, name='listar_citas'),
    
    # Ruta para registrar un diagnóstico
    path('diagnosticos/registro/<int:cita_id>/', views.registrar_diagnostico, name='registrar_diagnostico'),
    
    # Ruta para emitir una receta médica
    path('recetas/emitir/<int:cita_id>/', views.emitir_receta, name='emitir_receta'),
    
    # Ruta para registrar una calificación
    path('calificaciones/registro/<int:cita_id>/', views.registrar_calificacion, name='registrar_calificacion'),
    
    
]
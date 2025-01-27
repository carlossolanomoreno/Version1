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
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    # Administración de Django
    

    
    path('admin/', admin.site.urls),

    # Rutas específicas de pacientes
    path('paciente/', include('citas.paciente.urls')),

    # Rutas específicas de administrador
    path('administrador/', include('citas.administrador.urls')),

    # Rutas específicas de médicos
    path('medico/', include('citas.medico.urls')),
    
    
    # Rutas específicas de secretaria
    path('secretaria/', include('citas.secretaria.urls')),


    # Logout para cualquier tipo de usuario
    path('logout/', LogoutView.as_view(), name='user_logout'),

    # Página principal del sistema
    path('', views.home, name='home'),
]

# Configuración de archivos multimedia en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


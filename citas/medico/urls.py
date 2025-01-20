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

urlpatterns = [
    # Página principal de médicos
    path('', views.home, name='home'),
    path('login/', views.login_medico, name='login_medico'),
    path('dashboard-medico/', views.dashboard_medico, name='dashboard_medico'),
    path('perfil/', views.perfil_medico, name='perfil_medico'),
    path('agenda/', views.ver_agenda, name='ver_agenda'),
    path('historial-clinico/', views.ver_historial_clinico, name='ver_historial_clinico'),
    path('diagnostico/', views.generar_diagnostico, name='generar_diagnostico'),
    path('receta/', views.generar_receta, name='generar_receta'),
    path('examen/', views.solicitar_examen, name='solicitar_examen'),
]



from django.urls import path
from . import views
from .views import (
    EstadisticasDashboardAPIView,
    registrar_administrador_view,
    recuperar_credenciales,
    ExportarReporteAPIView,
    login_admin_view,
)

urlpatterns = [
    
    path('inicio/', views.inicio, name='inicio'),
    # URL para registrar administrador
    path('registrar/', registrar_administrador_view, name='registro_administrador'),
    
    # URL para login de administrador
    path('login/', login_admin_view, name='login_admin'),
    
    path('recuperar/', recuperar_credenciales, name='recuperar_credenciales_administrador'),
    
    # URL para el dashboard del administrador
    path('dashboard/', views.administrador_dashboard_view, name='administrador_dashboard'),
    
    # URL para exportar estadísticas
    path('exportar-estadisticas/', views.exportar_estadisticas, name='exportar_estadisticas'),
    path('generar-reporte/', views.GenerarReporte.generar_reporte, name='generar_reporte'),
      
    # URL para gestionar usuarios
    path('dashboard/', views.administrador_dashboard_view, name='administrador_dashboard'),
    path('registrar_paciente/', views.registrar_paciente_admin, name='registrar_paciente_admin'),
    path('registrar/secretaria/', views.registrar_secretaria_admin, name='registrar_secretaria_admin'),
    path('no_autorizado/', views.no_autorizado_view, name='no_autorizado'),  # Página de acceso no autorizado
    
    path('registrar_medico/', views.registrar_medico_admin, name='registro_medico_admin'),
    path('registrar_especialidad/<int:medico_id>/', views.registrar_especialidad_medico, name='registrar_especialidad_medico'),
    
    # API para estadísticas del dashboard
    path('api/dashboard-estadisticas/', EstadisticasDashboardAPIView.as_view(), name='api_dashboard_estadisticas'),
    
    
    # API para exportar reportes
    path('api/exportar-reporte/<str:formato>/', ExportarReporteAPIView.as_view(), name='api_exportar_reporte'),
    
  
    

   # Vista principal para gestionar las citas


    # Vista para agendar la cita
    path('agendar_citas/', views.agendar_citas, name='agendar_citas'),
    path('cargar_medicos/', views.cargar_medicos, name='cargar_medicos'),
    path('cita_agendada/', views.cita_agendada, name='cita_agendada'),

]






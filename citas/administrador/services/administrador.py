from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from citas.models import Usuario, Cita, Calificacion, Administrador,Estadisticas
from citas.forms import RegistroAdministradorForm
from citas.serializers import HorarioMedicoSerializer
import logging
from django.db.utils import IntegrityError
import csv
import xlwt
from django.http import HttpResponse
logger = logging.getLogger(__name__)
from django.db.models import Avg
import logging
from citas.models import Usuario, Estadisticas
logger = logging.getLogger(__name__)
    
    
    
# Registrar administrador 
def registrar_administrador_service(datos_formulario):
    form = RegistroAdministradorForm(datos_formulario)
    if form.is_valid():
        try:
            usuario = form.save(commit=False)
            usuario.tipo_usuario = 'Administrador'
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            Administrador.objects.create(usuario=usuario)
            return {"exito": True, "mensaje": "Administrador registrado exitosamente."}
        except IntegrityError as e:
            logger.exception("Error de integridad al registrar administrador: %s", e)
            return {"exito": False, "mensaje": "Error al guardar el administrador. Verifica los datos."}
        except Exception as e:
            logger.exception("Error inesperado al registrar administrador: %s", e)
            return {"exito": False, "mensaje": "Error inesperado."}
    return {"exito": False, "mensaje": "Datos del formulario inválidos."}


# Gestionar horario médico
def gestionar_horario_medico_service(request):
    serializer = HorarioMedicoSerializer(data=request.data)
    if serializer.is_valid():
        try:
            horario = serializer.save()
            return Response({"mensaje": "Horario guardado correctamente."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Error gestionando horario médico: %s", e)
            return Response({"mensaje": f"Error al guardar el horario: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"mensaje": "Datos inválidos. Verifique la información ingresada."}, status=status.HTTP_400_BAD_REQUEST)

# Autenticar administrador
def autenticar_administrador(cedula, password, request):
    usuario = Usuario.objects.filter(cedula=cedula).first()
    if not usuario or not usuario.check_password(password):
        return {"exito": False, "mensaje": "Credenciales incorrectas."}
    if usuario.tipo_usuario != 'Administrador':
        return {"exito": False, "mensaje": "No tienes permisos para acceder a esta página."}

    login(request, usuario)
    return {"exito": True}

# Generar datos para el dashboard
def generar_dashboard_data():
    try:
        # Citas Pendientes
        citas_pendientes = Cita.objects.filter(estado='Pendiente').count()

        # Citas Finalizadas
        citas_finalizadas = Cita.objects.filter(estado='Finalizada').count()

        # Citas Canceladas (si tienes citas canceladas)
        citas_canceladas = Cita.objects.filter(estado='Cancelada').count()

        # Total de Pacientes (contar pacientes únicos)
        total_pacientes = Cita.objects.values('paciente').distinct().count()

        # Total de Calificaciones
        total_calificaciones = Calificacion.objects.count()

        # Promedio de Calificación
        promedio_calificacion = Calificacion.objects.aggregate(promedio=Avg('calificacion'))['promedio'] or 0

        return {
            'citas_pendientes': citas_pendientes,
            'citas_finalizadas': citas_finalizadas,
            'citas_canceladas': citas_canceladas,
            'total_pacientes': total_pacientes,
            'total_calificaciones': total_calificaciones,
            'promedio_calificacion': promedio_calificacion,
        }

    except Exception as e:
        logger.exception("Error generando datos para el dashboard: %s", e)
        return {
            'citas_pendientes': 0,
            'citas_finalizadas': 0,
            'citas_canceladas': 0,
            'total_pacientes': 0,
            'total_calificaciones': 0,
            'promedio_calificacion': 0,
            'error': str(e),
        }




# Exportar reporte
def exportar_reporte(formato):
    reporte = Estadisticas.objects.last()
    if not reporte:
        raise ValueError("No hay estadísticas disponibles para exportar.")

    formatos_permitidos = ["csv", "xls"]
    if formato not in formatos_permitidos:
        raise ValueError(f"Formato no soportado. Use uno de los siguientes: {', '.join(formatos_permitidos)}")

    # Exportar en CSV
    if formato == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte.csv"'
        writer = csv.writer(response)
        writer.writerow(["Nombre", "Total Pacientes", "Total Citas", "Promedio Calificación"])
        writer.writerow([reporte.nombre_reporte, reporte.total_pacientes, reporte.total_citas, reporte.promedio_calificacion])
        return response

    # Exportar en XLS
    if formato == "xls":
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="reporte.xls"'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Reporte')
        ws.write(0, 0, "Nombre")
        ws.write(0, 1, "Total Pacientes")
        ws.write(0, 2, "Total Citas")
        ws.write(0, 3, "Citas Pendientes")
        ws.write(0, 4, "Citas Finalizadas")
        ws.write(0, 5, "Citas Canceladas")
        ws.write(0, 6, "Promedio Calificación")
        ws.write(1, 0, reporte.nombre_reporte)
        ws.write(1, 1, reporte.total_pacientes)
        ws.write(1, 2, reporte.total_citas)
        ws.write(1, 3, reporte.citas_pendientes)
        ws.write(1, 4, reporte.citas_finalizadas)
        ws.write(1, 5, reporte.citas_canceladas)
        ws.write(1, 6, reporte.promedio_calificacion)
        wb.save(response)
        return response






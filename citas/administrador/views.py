from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from citas.models import Usuario, Administrador, Especialidad, Cita, HorarioMedico, Estadisticas, Medico, Secretaria, Paciente
from citas.forms import RegistroAdministradorForm, EspecialidadForm, RegistroPacienteForm, MedicoForm, SecretariaForm, AgendarCitaForm
from django.contrib.auth import get_user_model
from citas.decorators import administrador_required
from citas.administrador.services.administrador import (
    exportar_reporte,
    generar_dashboard_data,
    autenticar_administrador
)
from django.http import JsonResponse
import requests
import os
import random
from django.utils import timezone
User = get_user_model()
from citas.models import crear_turnos


# Verifica si el usuario es administrador
def es_administrador(user):
    return user.is_authenticated and user.tipo_usuario == 'Administrador'

@login_required
@user_passes_test(es_administrador)
def administrador_dashboard_view(request): 
    return HttpResponse("No autorizado.", status=403)

def no_autorizado_view(request):
    return render(request, 'administrador/no_autorizado.html', {})


# Login de administrador
def login_admin_view(request):
    if request.method == "POST":
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')

        if not cedula or not password:
            messages.error(request, "Por favor, ingresa cédula y contraseña.")
            return render(request, 'administrador/login_admin.html')

        resultado = autenticar_administrador(cedula, password, request)
        if resultado["exito"]:
            return redirect('administrador_dashboard')  # Redirige al dashboard del administrador
        else:
            messages.error(request, resultado["mensaje"])

    return render(request, 'administrador/login_admin.html')

# Registrar administrador
def registrar_administrador_view(request):
    if request.method == 'POST':
        form = RegistroAdministradorForm(request.POST)
        if form.is_valid():
            try:
                usuario = form.save(commit=False)
                usuario.tipo_usuario = 'Administrador'
                usuario.set_password(form.cleaned_data['password'])
                usuario.save()
                Administrador.objects.create(usuario=usuario)
                messages.success(request, "Registro exitoso. Inicia sesión a continuación.")
                return redirect('login_admin')  # Redirige al login de administrador
            except IntegrityError as e:
                messages.error(request, "Error de integridad. Verifica los datos e inténtalo nuevamente.")
            except Exception as e:
                messages.error(request, "Ha ocurrido un error inesperado. Inténtalo nuevamente.")
        else:
            messages.error(request, "Formulario inválido. Revisa los datos ingresados.")
    else:
        form = RegistroAdministradorForm()

    return render(request, 'administrador/registro_administrador.html', {'form': form})

# Enviar mensaje a Telegram
def enviar_mensaje_telegram(chat_id, mensaje, token):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': mensaje}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error al enviar mensaje: {http_err}")
        return False
    except requests.exceptions.RequestException as req_err:
        print(f"Error de red al enviar mensaje: {req_err}")
        return False

# Recuperar credenciales
def recuperar_credenciales(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        if not cedula:
            return JsonResponse({'exito': False, 'mensaje': 'Debes proporcionar una cédula.'}, status=400)

        try:
            usuario = Usuario.objects.get(cedula=cedula)

            if not usuario.chat_id or usuario.chat_id.strip() == "":
                return JsonResponse({'exito': False, 'mensaje': 'El usuario no tiene un chat_id asociado.'}, status=404)

            nueva_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            usuario.set_password(nueva_password)
            usuario.save()

            mensaje = (
                f"Hola {usuario.nombres},\n"
                f"Tu nueva contraseña temporal es: {nueva_password}\n"
                f"Por favor, cámbiala después de iniciar sesión."
            )
            token_telegram = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token_telegram:
                return JsonResponse({'exito': False, 'mensaje': 'Token de Telegram no configurado.'}, status=500)

            if enviar_mensaje_telegram(usuario.chat_id, mensaje, token_telegram):
                return JsonResponse({'exito': True, 'mensaje': 'Se ha enviado una nueva contraseña a tu Telegram.'})
            else:
                return JsonResponse({'exito': False, 'mensaje': 'No se pudo enviar el mensaje a través de Telegram.'}, status=500)

        except Usuario.DoesNotExist:
            return JsonResponse({'exito': False, 'mensaje': 'La cédula no está registrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'exito': False, 'mensaje': f'Error inesperado: {str(e)}'}, status=500)

    return render(request, 'administrador/recuperar_credenciales_administrador.html')



@login_required
@administrador_required
def administrador_dashboard_view(request):
    """
    Muestra el dashboard principal del administrador con estadísticas relevantes.
    """
    # Validar si el usuario tiene el tipo 'Administrador'
    if not hasattr(request.user, 'tipo_usuario') or request.user.tipo_usuario != 'Administrador':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('no_autorizado')

    # Generar los datos del dashboard
    context = generar_dashboard_data()
    if 'error' in context:
        messages.error(request, f"Error al cargar el dashboard: {context['error']}")
    
    # Renderizar la plantilla con el contexto generado
    return render(request, "administrador/administrador_dashboard.html", context)


@login_required
def registrar_paciente_admin(request):
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            # Asignar grupo 'Pacientes'
            pacientes_group, _ = Group.objects.get_or_create(name='Pacientes')
            usuario.groups.add(pacientes_group)

            Paciente.objects.create(usuario=usuario)

            messages.success(request, "Paciente registrado exitosamente.")
            return redirect('administrador_dashboard')  # Redirige al dashboard del administrador
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")
    else:
        form = RegistroPacienteForm()

    return render(request, 'administrador/registro_paciente_admin.html', {'form': form})

@login_required
def registrar_secretaria_admin(request):
    if request.method == 'POST':
        form = SecretariaForm(request.POST)
        if form.is_valid():
            # Crear usuario como secretaria
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()

            # Asignar grupo 'Pacientes'
            secretarias_group, _ = Group.objects.get_or_create(name='Secretarias')
            usuario.groups.add(secretarias_group)
            
            Secretaria.objects.create(usuario=usuario)

            messages.success(request, 'Secretaria registrada exitosamente.')
            return redirect('administrador_dashboard')  # Ajustar a la URL del dashboard
        else:
            # Mostrar todos los errores de forma más detallada
            for field, errors in form.errors.items():
                print(f'Error en el campo {field}: {errors}')
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = SecretariaForm()

    return render(request, 'administrador/registro_secretaria_admin.html', {'form': form})

# En views.py o en el archivo correspondiente
# En views.py
@login_required
def registrar_medico_admin(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            # Crear usuario como médico
            usuario = form.save(commit=False)
            usuario.tipo_usuario = 'Medico'
            usuario.set_password(form.cleaned_data['password'])  # Asegúrate de usar set_password
            usuario.username = form.cleaned_data['cedula']  # Usando la cédula como username
            usuario.save()

            # Crear entrada específica del médico
            medico = Medico.objects.create(usuario=usuario)

            # Llamar a la función para crear los turnos automáticamente
            try:
                crear_turnos(medico)
                messages.success(request, 'Médico registrado y turnos generados exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al generar los turnos: {e}')
                print(f"Error al crear los turnos: {e}")

            return redirect('registrar_especialidad_medico', medico_id=medico.id)

        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = MedicoForm()

    return render(request, 'administrador/registro_medico_admin.html', {'form': form})



@login_required 
@user_passes_test(es_administrador)
def registrar_especialidad_medico(request, medico_id):
    medico = Medico.objects.get(id=medico_id)  # Obtén el médico registrado

    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        
        if form.is_valid():  # Verifica si el formulario es válido
            # Guardar la especialidad
            especialidad = form.save(commit=False)  # No guardar aún en la DB
            especialidad.save()  # Guardamos la especialidad
            print("Especialidad guardada:", especialidad)  # Para depuración

            # Asociar la especialidad con el médico (ManyToManyField)
            medico.especialidades.add(especialidad)  # Usamos `add()` para una relación ManyToMany
            medico.save()

            messages.success(request, 'Especialidad registrada exitosamente.')
            return redirect('administrador_dashboard')  # Redirigir al dashboard
        else:
            # Si el formulario no es válido, imprime los errores para ver qué está fallando
            print("Errores del formulario:", form.errors)
    else:
        form = EspecialidadForm()

    return render(request, 'administrador/registrar_especialidad_medico.html', {'form': form, 'medico': medico})


@login_required
def agendar_citas(request):
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            # Se asocia el paciente seleccionado
            cita.paciente = form.cleaned_data['paciente']
            cita.save()
            return redirect('cita_agendada')  # Redirigir a una página que confirme que la cita fue agendada
    else:
        form = AgendarCitaForm()

    return render(request, 'administrador/agendar_citas.html', {'form': form})




 
def cargar_medicos(request):
    especialidad_id = request.GET.get('especialidad_id')
    try:
        especialidad = Especialidad.objects.get(id=especialidad_id)
        medicos = Medico.objects.filter(especialidades=especialidad)
        medico_data = [{'id': medico.id, 'nombre': f"{medico.usuario.nombres} {medico.usuario.apellidos}"} for medico in medicos]
        return JsonResponse({'medicos': medico_data})
    except Especialidad.DoesNotExist:
        return JsonResponse({'error': 'Especialidad no encontrada'}, status=400)
 

def cargar_horarios(request):
    medico_id = request.GET.get('medico_id')
    try:
        # Busca el médico correspondiente
        medico = Usuario.objects.get(id=medico_id, tipo_usuario='Médico')

        # Filtra horarios solo por el médico y los tres meses
        hoy = timezone.now()
        # Establecer el primer día del mes actual
        fecha_inicio = hoy.replace(day=1)  # Primer día del mes actual
        # Establecer el primer día del cuarto mes
        fecha_fin = (fecha_inicio.replace(month=fecha_inicio.month + 3) 
             if fecha_inicio.month <= 9 
             else fecha_inicio.replace(year=fecha_inicio.year + 1, month=(fecha_inicio.month + 3 - 12)))


        # Filtra los horarios para los tres meses
        horarios = HorarioMedico.objects.filter(
            medico=medico,
            fecha__gte=fecha_inicio,
            fecha__lt=fecha_fin
        )

        # Genera los datos de respuesta, incluyendo la fecha y el mes
        horario_data = [
            {
                'id': horario.id,
                'dia': horario.dia,
                'fecha': horario.fecha.strftime('%d/%m/%Y'),  # Fecha completa (día/mes/año)
                'mes': horario.fecha.strftime('%B'),  # Nombre del mes (por ejemplo, "Enero")
                'ano': horario.fecha.strftime('%Y'),  # Año
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
            }
            for horario in horarios
        ]

        return JsonResponse({'horarios': horario_data})

    except Medico.DoesNotExist:
        return JsonResponse({'error': 'Médico no encontrado'}, status=400)
    
       
    
@login_required
def cita_agendada(request):
    try:
        # El administrador debe seleccionar al paciente al que se le ha agendado la cita
        # Mostrar la última cita agendada para todos los pacientes
        cita = Cita.objects.last()  # Obtiene la última cita agendada de todos los pacientes

        # En caso de no haber citas agendadas
        if not cita:
            return HttpResponse('No hay citas agendadas.', status=404)

        return render(request, 'administrador/cita_agendada.html', {'cita': cita})
    except Exception as e:
        # Capturar cualquier otro tipo de excepción
        return HttpResponse(f'Error inesperado: {str(e)}', status=500)


def listar_citas(request):
    # Recuperar todas las citas médicas ordenadas por fecha y hora de inicio
    citas = Cita.objects.all().order_by('horario_medico')
    return render(request, 'administrador/listar_citas.html', {'citas': citas})
    



# Exportar estadísticas (CSV, XLS, PDF)
@login_required
def exportar_estadisticas(request):
    """
    Exporta las estadísticas en el formato solicitado.
    """
    formato = request.GET.get('formato', '').lower()
    context = generar_dashboard_data()

    if 'error' in context:
        return JsonResponse({'error': f"Error al generar estadísticas: {context['error']}"}, status=400)

    try:
        return exportar_reporte(formato)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Error inesperado: {str(e)}"}, status=500)

class GenerarReporte:
    """
    Vista que genera el reporte de estadísticas y lo renderiza en una página HTML.
    """
    @staticmethod
    def generar_reporte(request):
        try:
            reporte = Estadisticas.objects.last()  # Último reporte en la base de datos
            if not reporte:
                return render(request, 'administrador/generar_reporte.html', {'mensaje': "No hay estadísticas disponibles."})

            # Se pasan los datos a la plantilla
            context = {
                "nombre_reporte": reporte.nombre_reporte,
                "fecha_creacion": reporte.fecha_creacion,
                "total_pacientes": reporte.total_pacientes,
                "total_citas": reporte.total_citas,
                "citas_pendientes": reporte.citas_pendientes,
                "citas_finalizadas": reporte.citas_finalizadas,
                "citas_canceladas": reporte.citas_canceladas,
                "total_diagnosticos": reporte.total_diagnosticos,
                "promedio_calificacion": reporte.promedio_calificacion,
            }
            return render(request, 'administrador/generar_reporte.html', context)

        except Exception as e:
            return render(request, 'administrador/generar_reporte.html', {'error': f"Error al obtener estadísticas: {str(e)}"})


class EstadisticasDashboardAPIView(APIView):
    """
    API que retorna las estadísticas para el dashboard del administrador.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            reporte = Estadisticas.objects.last()
            if not reporte:
                return Response({"mensaje": "No hay estadísticas disponibles."}, status=200)
            datos = {
                "nombre_reporte": reporte.nombre_reporte,
                "fecha_creacion": reporte.fecha_creacion,
                "total_pacientes": reporte.total_pacientes,
                "total_citas": reporte.total_citas,
                "citas_pendientes": reporte.citas_pendientes,
                "citas_finalizadas": reporte.citas_finalizadas,
                "citas_canceladas": reporte.citas_canceladas,
                "total_diagnosticos": reporte.total_diagnosticos,
                "promedio_calificacion": reporte.promedio_calificacion,
            }
            return Response(datos, status=200)
        except Exception as e:
            return Response({"error": f"Error al obtener estadísticas: {str(e)}"}, status=500)

# API para exportar reportes
class ExportarReporteAPIView(APIView):
    """
    API para exportar reportes en un formato específico.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, formato):
        try:
            return exportar_reporte(formato)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=500)




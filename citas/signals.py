from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Paciente, Diagnostico, Cita, Estadisticas, Calificacion, HistorialClinico, Usuario
from datetime import datetime
from django.contrib.auth.models import Group

# Actualizar total_pacientes
@receiver(post_save, sender=Paciente)
def actualizar_total_pacientes(sender, instance, created, **kwargs):
    if created:
        estadisticas, _ = Estadisticas.objects.get_or_create(id=1)
        estadisticas.total_pacientes += 1
        estadisticas.save()

# Actualizar total_diagnosticos
@receiver(post_save, sender=Diagnostico)
def actualizar_total_diagnosticos(sender, instance, created, **kwargs):
    if created:
        estadisticas, _ = Estadisticas.objects.get_or_create(id=1)
        estadisticas.total_diagnosticos += 1
        estadisticas.save()

# Actualizar citas (totales, pendientes, finalizadas, canceladas)
@receiver(post_save, sender=Cita)
def actualizar_citas(sender, instance, created, **kwargs):
    estadisticas, _ = Estadisticas.objects.get_or_create(id=1)
    if created:
        estadisticas.total_citas += 1
        if instance.estado == 'Pendiente':
            estadisticas.citas_pendientes += 1
        elif instance.estado == 'Finalizada':
            estadisticas.citas_finalizadas += 1
        elif instance.estado == 'Cancelada':
            estadisticas.citas_canceladas += 1
    else:
        # Si se actualiza el estado de la cita, ajustar los contadores
        estados_anterior = instance._pre_save_estado
        if estados_anterior != instance.estado:
            if estados_anterior == 'Pendiente':
                estadisticas.citas_pendientes -= 1
            elif estados_anterior == 'Finalizada':
                estadisticas.citas_finalizadas -= 1
            elif estados_anterior == 'Cancelada':
                estadisticas.citas_canceladas -= 1
            
            if instance.estado == 'Pendiente':
                estadisticas.citas_pendientes += 1
            elif instance.estado == 'Finalizada':
                estadisticas.citas_finalizadas += 1
            elif instance.estado == 'Cancelada':
                estadisticas.citas_canceladas += 1
    estadisticas.save()

@receiver(pre_save, sender=Cita)
def guardar_estado_anterior(sender, instance, **kwargs):
    # Guardar el estado anterior para referencia en la actualización
    if instance.pk:
        instance._pre_save_estado = Cita.objects.get(pk=instance.pk).estado
    else:
        instance._pre_save_estado = None

# Actualizar citas por día, semana, mes, año
@receiver(post_save, sender=Cita)
def actualizar_citas_por_tiempo(sender, instance, created, **kwargs):
    if created:
        estadisticas, _ = Estadisticas.objects.get_or_create(id=1)
        fecha = instance.horario_medico.dia
    
    # Verifica si 'fecha' es una cadena y conviértela a fecha
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            # Si no se puede convertir a fecha, maneja el error (por ejemplo, logging)
            print("Error al convertir la fecha")
            return
        # Actualizar citas por día
        citas_dia = estadisticas.citas_por_dia.get(str(fecha), 0)
        estadisticas.citas_por_dia[str(fecha)] = citas_dia + 1

        # Similar para citas por semana, mes, año
        semana = fecha.isocalendar()[1]
        mes = fecha.month
        ano = fecha.year

        citas_semana = estadisticas.citas_por_semana.get(str(semana), 0)
        estadisticas.citas_por_semana[str(semana)] = citas_semana + 1

        citas_mes = estadisticas.citas_por_mes.get(str(mes), 0)
        estadisticas.citas_por_mes[str(mes)] = citas_mes + 1

        citas_ano = estadisticas.citas_por_ano.get(str(ano), 0)
        estadisticas.citas_por_ano[str(ano)] = citas_ano + 1

        estadisticas.save()

# Actualizar promedio de calificaciones y calificaciones por médico
@receiver(post_save, sender=Calificacion)
def actualizar_calificaciones(sender, instance, created, **kwargs):
    estadisticas, _ = Estadisticas.objects.get_or_create(id=1)
    if created:
        # Calcular promedio de calificaciones
        total_calificaciones = Calificacion.objects.count()
        suma_calificaciones = sum(c.calificacion for c in Calificacion.objects.all())
        estadisticas.promedio_calificacion = suma_calificaciones / total_calificaciones

        # Actualizar calificaciones por médico
        medico_id = instance.medico.id
        calificaciones_medico = estadisticas.calificaciones_por_medico.get(str(medico_id), [])
        calificaciones_medico.append(instance.calificacion)
        estadisticas.calificaciones_por_medico[str(medico_id)] = calificaciones_medico

        estadisticas.save()
        
@receiver(post_save, sender=Paciente)
def crear_historial_clinico(sender, instance, created, **kwargs):
    if created:
        HistorialClinico.objects.create(paciente=instance)      
        
def crear_estadisticas_iniciales():
    """
    Verifica si existe un registro en la tabla Estadisticas.
    Si no existe, crea un registro inicial con valores predeterminados.
    """    
    if not Estadisticas.objects.exists():
        Estadisticas.objects.create(
            nombre_reporte="Estadísticas Generales",
            total_pacientes=0,
            total_diagnosticos=0,
            total_citas=0,
            citas_pendientes=0,
            citas_finalizadas=0,
            citas_canceladas=0,
            promedio_calificacion=0.0,
            pacientes_atendidos_por_especialidad={},
            citas_por_dia={},
            citas_por_semana={},
            citas_por_mes={},
            citas_por_ano={},
            calificaciones_por_medico={},
        )
        print("Registro inicial creado.")
        
        
        
@receiver(post_save, sender=Usuario)
def asignar_usuario_al_grupo(sender, instance, created, **kwargs):
    if created:  # Solo si el usuario ha sido creado
        # Obtener o crear el grupo "Secretarias"
        grupo_secretarias = Group.objects.filter(name="Secretarias").first()
        if not grupo_secretarias:
            grupo_secretarias = Group.objects.create(name="Secretarias")

        # Asignar al usuario al grupo "Secretarias"
        instance.groups.add(grupo_secretarias)
        instance.save()
        print(f"El usuario {instance} ha sido asignado al grupo 'Secretarias'.")

    

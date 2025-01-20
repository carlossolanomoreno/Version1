from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.db.models.signals import post_migrate
from django.contrib.auth.password_validation import validate_password
from django.dispatch import receiver
from django.utils import timezone
from typing import Type
from django.core.exceptions import ValidationError
import datetime
from django.conf import settings
import random
import string
import requests
import os
from PIL import Image
from django.conf import settings
from datetime import timedelta, time, datetime

# Administrador personalizado para crear usuarios
class UsuarioManager(BaseUserManager):
    def create_user(self, cedula, correo_electronico, tipo_usuario, password=None, **extra_fields):
        """
        Crea y guarda un usuario con la cédula, correo electrónico y tipo de usuario proporcionados.
        """
        if not cedula:
            raise ValueError("La cédula es obligatoria.")
        if not correo_electronico:
            raise ValueError("El correo electrónico es obligatorio.")

        correo_electronico = self.normalize_email(correo_electronico)

        user = self.model(
            cedula=cedula,
            correo_electronico=correo_electronico,
            tipo_usuario=tipo_usuario,
            **extra_fields,
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)

        if tipo_usuario == 'Paciente':
            Paciente.objects.create(usuario=user)

        return user

    def create_superuser(self, cedula, correo_electronico, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con la cédula y correo proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(cedula, correo_electronico, 'Administrador', password, **extra_fields)

class Usuario(AbstractUser, PermissionsMixin):
    cedula = models.CharField(max_length=10, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True, blank=False, null=False)
    chat_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=150, blank=True)
    ciudad_residencia = models.CharField(max_length=50, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, default='Otro')
    
    TIPO_USUARIO_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Medico', 'Medico'),
        ('Secretaria', 'Secretaria'),
        ('Paciente', 'Paciente'),
    ]
    tipo_usuario = models.CharField(max_length=50, choices=TIPO_USUARIO_CHOICES)
    
    USERNAME_FIELD = 'cedula'
    REQUIRED_FIELDS = ['correo_electronico']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.cedula})"
    
#Paciente
class Paciente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    def __str__(self):
        return f"Paciente: {self.usuario.nombres} {self.usuario.apellidos}"

class Administrador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return f"Administrador: {self.usuario.nombres} {self.usuario.apellidos}"

# Especialidad
class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100)
    descripcion_especialidad = models.TextField()
    fecha_registro = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    estado = models.CharField(
        max_length=20,
        choices=[('Activa', 'Activa'), ('Inactiva', 'Inactiva')],
        default='Activa'
    )

    def __str__(self):
  
        return self.nombre_especialidad   


# Medico

class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    especialidades = models.ManyToManyField(Especialidad, through='CitasMedicoEspecialidad')
    
    def __str__(self):
        return f"Médico: {self.usuario.nombres} {self.usuario.apellidos}"



class CitasMedicoEspecialidad(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.BooleanField(default=True)  # Relación activa o inactiva
    observaciones = models.TextField(blank=True, null=True)  # Campo opcional para detalles adicionales

    def __str__(self):
        return f'{self.medico} - {self.especialidad}'

    class Meta:
        unique_together = ('medico', 'especialidad')  # Asegura que no haya duplicados

# Horario Medico 
class HorarioMedico(models.Model):
    medico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=9, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f'{self.dia} de {self.hora_inicio} a {self.hora_fin}'
    
    
from citas.models import HorarioMedico, Usuario

def crear_turnos():
    horarios = []
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    horas_mañana = [time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30)]
    horas_tarde = [time(16, 0), time(16, 30), time(17, 0), time(17, 30)]

    # Obtén todos los médicos registrados en la base de datos
    medicos = Usuario.objects.filter(tipo_usuario='Médico')

    if not medicos.exists():
        raise ValueError("No hay médicos registrados en la base de datos.")

    for medico in medicos:
        for dia in dias:
            for hora_inicio in horas_mañana + horas_tarde:
                hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=30)).time()
                horarios.append(HorarioMedico(medico=medico, dia=dia, hora_inicio=hora_inicio, hora_fin=hora_fin))

    # Insertar los horarios generados en la base de datos
    HorarioMedico.objects.bulk_create(horarios)


    
    
# Agenda
class Agenda(models.Model):
    medico = models.OneToOneField(Medico, on_delete=models.CASCADE, related_name='agenda')
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Última vez que se actualizó la agenda

    def citas_pendientes(self):
        return self.medico.citas.filter(estado='Pendiente')
    

    def citas_por_fecha(self, fecha):
        return self.medico.citas.filter(fecha_cita=fecha)

    def __str__(self):
        return f"Agenda de {self.medico.usuario.nombres} {self.medico.usuario.apellidos}"

# Cita
class Cita(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="citas")
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name="citas")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="citas")
    horario_medico = models.ForeignKey(HorarioMedico, on_delete=models.SET_DEFAULT, default=1)  # Aquí está el horario médico
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('En Atención', 'En Atención'),
        ('Finalizada', 'Finalizada')
    ], default='Pendiente')

    def __str__(self):
        return f"Cita {self.especialidad.nombre_especialidad} con {self.medico.usuario.nombres} - {self.horario_medico.dia} {self.horario_medico.hora_inicio}-{self.horario_medico.hora_fin}"


      
# Historial Clinico
class HistorialClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historia')
    fecha_creacion = models.DateField(auto_now_add=True)
    antecedentes = models.TextField(null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    enfermedades_cronicas = models.TextField(null=True, blank=True)   
    
    def __str__(self):
        return f"Historial Clínico de {self.paciente.usuario.nombres}"
    
# Diagnostico
class Diagnostico(models.Model):
    cita = models.OneToOneField('Cita', on_delete=models.CASCADE, related_name='diagnostico')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    proximo_control = models.DateField(null=True, blank=True)  # Nuevo campo

    def __str__(self):
        return f"Diagnóstico para cita {self.cita.id}"
    
# ExamenMedico    
class ExamenMedico(models.Model):
    cita = models.ForeignKey('Cita', on_delete=models.CASCADE, related_name='examenes')
    tipo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Examen: {self.tipo} - Cita {self.cita.id}"
 
# RecetaMedica    
class RecetaMedica(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='recetas')
    medicamentos = models.TextField()  # Lista de medicamentos y dosis
    indicaciones = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)   
    
    def __str__(self):
        return f"Receta médica para cita {self.cita.id}"
    
    
# Secretaria
class Secretaria(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Secretaria: {self.usuario.nombres} {self.usuario.apellidos}"


    def agendar_cita(self, especialidad, medico, paciente, fecha, hora):
        """Agendar una cita para un paciente con un médico."""
        from datetime import datetime

        # Validar disponibilidad del médico
        horarios_disponibles = HorarioMedico.objects.filter(
            medico=medico,
            fecha=fecha,
            hora_inicio__lte=hora,
            hora_fin__gte=hora,
            estado="Disponible"
        )
        if not horarios_disponibles.exists():
            raise ValueError("El médico no está disponible en la fecha y hora solicitadas.")

        # Verificar si ya existe una cita confirmada en ese horario
        if Cita.objects.filter(
            medico=medico,
            fecha_cita=fecha,
            hora_cita=hora,
            estado="Confirmada"
        ).exists():
            raise ValueError("Ya existe una cita confirmada para ese horario.")

        # Crear la cita
        cita = Cita.objects.create(
            medico=medico,
            especialidad=especialidad,
            paciente=paciente,
            fecha_cita=fecha,
            hora_cita=hora,
            estado="Confirmada"
        )

        # Cambiar el estado de la disponibilidad del horario
        horarios_disponibles.update(estado="No Disponible")

        # Enviar mensaje de confirmación por Telegram
        self.enviar_mensaje_telegram(paciente, f"Cita programada: {especialidad.nombre_especialidad} con {medico.usuario.nombres} el {fecha} a las {hora}.")
        return cita

    def cancelar_cita(self, cita):
        """Cancelar una cita previamente agendada."""
        if cita.estado == "Confirmada":
            cita.estado = "Cancelada"
            cita.save()
            # Cambiar el estado del horario a disponible
            HorarioMedico.objects.filter(
                medico=cita.medico, 
                fecha=cita.fecha_cita, 
                hora_inicio=cita.hora_cita
                ).update(estado="Disponible")

            # Notificar al paciente sobre la cancelación
            self.enviar_mensaje_telegram(cita.paciente, f"Tu cita con el médico {cita.medico.usuario.nombres} ha sido cancelada.")
        else:
            raise ValueError("La cita no puede ser cancelada porque no está confirmada.")

    def enviar_mensaje_telegram(self, paciente, mensaje):
        """Enviar mensaje de notificación a través de Telegram."""
        if not paciente.usuario.chat_id:
            raise ValueError("El paciente no tiene un chat_id registrado para recibir mensajes.")

        token = os.getenv('TELEGRAM_BOT_TOKEN')
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {'chat_id': paciente.usuario.chat_id, 'text': mensaje}

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error al enviar mensaje de Telegram: {e}")

 
# Calificación
class Calificacion(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='calificacion', null=True, blank=True)
    calificacion = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=3)  # Calificación del 1 al 5
    comentario = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calificación {self.calificacion} - Cita: {self.cita.fecha_cita}"



class Estadisticas(models.Model):
    # Campos generales
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre_reporte = models.CharField(max_length=100)  # Nombre identificador del reporte

    # Datos relacionados con Pacientes
    total_pacientes = models.PositiveIntegerField(default=0)

    # Datos relacionados con Citas
    total_citas = models.PositiveIntegerField(default=0)
    citas_pendientes = models.PositiveIntegerField(default=0)
    citas_finalizadas = models.PositiveIntegerField(default=0)
    citas_canceladas = models.PositiveIntegerField(default=0)

    # Datos relacionados con Diagnósticos
    total_diagnosticos = models.PositiveIntegerField(default=0)

    # Datos relacionados con Calificaciones
    promedio_calificacion = models.FloatField(default=0.0)

    def __str__(self):
        return f"Reporte Estadístico: {self.nombre_reporte} ({self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')})"

    @classmethod
    def generar_estadisticas(cls, nombre_reporte="Reporte General"):
        """
        Método para generar datos agregados y guardarlos en el modelo.
        """
        try:
            # Calcular métricas generales
            total_pacientes = Paciente.objects.count()
            total_citas = Cita.objects.count()
            citas_pendientes = Cita.objects.filter(estado="Pendiente").count()
            citas_finalizadas = Cita.objects.filter(estado="Finalizada").count()
            citas_canceladas = Cita.objects.filter(estado="Cancelada").count()
            total_diagnosticos = Diagnostico.objects.count()
            promedio_calificacion = (
                Calificacion.objects.aggregate(promedio=Avg('calificacion'))['promedio'] or 0.0
            )

            # Crear y guardar un nuevo registro de estadísticas
            estadisticas = cls.objects.create(
                nombre_reporte=nombre_reporte,
                total_pacientes=total_pacientes,
                total_citas=total_citas,
                citas_pendientes=citas_pendientes,
                citas_finalizadas=citas_finalizadas,
                citas_canceladas=citas_canceladas,
                total_diagnosticos=total_diagnosticos,
                promedio_calificacion=promedio_calificacion,
            )
            return estadisticas
        except Exception as e:
            # Manejar errores y registrar
            logger.error(f"Error generando estadísticas: {e}")
            return None
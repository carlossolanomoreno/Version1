from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone

# Usuario
class Usuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    apellidos = models.CharField(max_length=100, default="Desconocido")
    nombres = models.CharField(max_length=100, default="Default Name")
    correo_electronico = models.EmailField(default="desconocido@dominio.com")
    telefono = models.CharField(max_length=20, default="Desconocido")
    direccion = models.CharField(max_length=150, default="Desconocida")
    ciudad_residencia = models.CharField(max_length=50, default="Desconocida")
    fecha_nacimiento = models.DateField(default=timezone.now)
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, default='Masculino')  # Valor predeterminado
    username = models.CharField(max_length=150, unique=True, default='default_username')
    password = models.CharField(max_length=128, default='default_password')
    
    groups = models.ManyToManyField(
        Group,
        related_name="usuario_groups",  # Nombre único
        blank=True,
        help_text="Los grupos a los que pertenece este usuario.",
        verbose_name="grupos",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_user_permissions",  # Nombre único
        blank=True,
        help_text="Permisos específicos para este usuario.",
        verbose_name="permisos de usuario",
    )

    def __str__(self):
        return f"{self.nombres}"

# Paciente
class Paciente(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE)

    def __str__(self):
        return f"Paciente: {self.usuario.nombres} {self.usuario.apellidos}"
    
# Especialidad
class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100)
    descripcion_especialidad = models.TextField()
    fecha_registro = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    estado = models.CharField(
        max_length=20, 
        choices=[
            ('Activa', 'Activa'),
            ('Inactiva', 'Inactiva')
        ], 
        default='Activa'
    )

    def __str__(self):
        return self.nombre_especialidad

# Medico
class Medico(models.Model):
    especialidad = models.ManyToManyField(Especialidad, related_name='medicos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    def __str__(self):
        return f"Dr. {self.usuario.nombres} {self.usuario.apellidos}"


# Horario Medico 
class HorarioMedico(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes')
    ])
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=20, 
        choices=[
            ('Disponible', 'Disponible'),
            ('No Disponible', 'No Disponible')
        ], 
        default='Disponible'
    )

    def __str__(self):
        return f"{self.medico.usuario.nombres} - {self.dia} ({self.hora_inicio}-{self.hora_fin})"


    
# Agenda
class Agenda(models.Model):
    medico = models.OneToOneField(Medico, on_delete=models.CASCADE, related_name='agenda')
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Última vez que se actualizó la agenda

    def __str__(self):
        return f"Agenda de {self.medico.usuario.nombres} {self.medico.usuario.apellidos}"

# Cita
class Cita(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha_cita = models.DateField()
    hora_cita = models.TimeField()
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('En Atención', 'En Atención'),
        ('Finalizada', 'Finalizada')
    ], default='Pendiente')
    
    def __str__(self):
        return f"Cita {self.especialidad.nombre_especialidad} con {self.medico.usuario.nombres} - {self.fecha_cita}"
    
      
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
    medico = models.ForeignKey('Medico', on_delete=models.CASCADE, related_name='diagnosticos_medico')
    descripcion = models.TextField()
    fecha = models.DateField(auto_now_add=True)  
    
    def __str__(self):
        return f"Diagnóstico - {self.cita}" 
    
# ExamenMedico    
class ExamenMedico(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='examenes')
    tipo = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    fecha_solicitud = models.DateField(auto_now_add=True)  
    
    def __str__(self):
        return f"Examen Médico ({self.tipo}) - {self.cita}"
 
# RecetaMedica    
class RecetaMedica(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='recetas')
    medicamentos = models.TextField()  # Lista de medicamentos y dosis
    indicaciones = models.TextField(null=True, blank=True)
    fecha_emision = models.DateField(auto_now_add=True)   
    
    def __str__(self):
        return f"Receta Médica - {self.cita}"
    
    
# Secretaria
class Secretaria(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    
    
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
        # Calcular métricas generales
        total_pacientes = Paciente.objects.count()
        total_citas = Cita.objects.count()
        citas_pendientes = Cita.objects.filter(estado="Pendiente").count()
        citas_finalizadas = Cita.objects.filter(estado="Finalizada").count()
        citas_canceladas = Cita.objects.filter(estado="Cancelada").count()
        total_diagnosticos = Diagnostico.objects.count()
        promedio_calificacion = (
            Calificacion.objects.aggregate(promedio=models.Avg('calificacion'))['promedio'] or 0.0
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
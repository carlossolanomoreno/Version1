from django.contrib import admin
from .models import Usuario, Paciente, Especialidad, Medico, HorarioMedico, Agenda, Cita, HistorialClinico, Diagnostico, ExamenMedico, RecetaMedica, Secretaria, Calificacion, Estadisticas

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(Medico)
admin.site.register(HorarioMedico)
admin.site.register(Agenda)
admin.site.register(Cita)
admin.site.register(HistorialClinico)
admin.site.register(Diagnostico)
admin.site.register(ExamenMedico)
admin.site.register(RecetaMedica)
admin.site.register(Secretaria)
admin.site.register(Calificacion)
admin.site.register(Estadisticas)
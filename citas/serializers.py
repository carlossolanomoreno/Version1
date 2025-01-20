from rest_framework import serializers
from .models import Cita, HorarioMedico

class AgendarCitaSerializer(serializers.Serializer):
    especialidad_id = serializers.IntegerField()
    medico_id = serializers.IntegerField()
    paciente_id = serializers.IntegerField()
    fecha = serializers.DateField()
    hora = serializers.TimeField()

class CancelarCitaSerializer(serializers.Serializer):
    cita_id = serializers.IntegerField()
    
    
class HorarioMedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioMedico
        fields = ['medico', 'dia', 'fecha', 'hora_inicio', 'hora_fin', 'estado']

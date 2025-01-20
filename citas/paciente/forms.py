from django import forms
from citas.models import Paciente


class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['foto_perfil']  # Asegúrate de que este campo existe en el modelo
        labels = {'foto_perfil': 'Subir foto de perfil'}
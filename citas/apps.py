from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citas'

    def ready(self):
        # Conectar la señal post_migrate
        post_migrate.connect(create_groups, sender=self)

def create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group

    groups = ['Medico', 'Secretaria', 'Administrador', 'Pacientes']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)

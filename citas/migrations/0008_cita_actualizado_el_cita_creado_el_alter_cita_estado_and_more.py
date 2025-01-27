# Generated by Django 5.1.1 on 2025-01-24 22:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas', '0007_horariomedico_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='actualizado_el',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cita',
            name='creado_el',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Finalizada', 'Finalizada'), ('Cancelada', 'Cancelada')], default='Pendiente', max_length=20),
        ),
        migrations.DeleteModel(
            name='Agenda',
        ),
    ]

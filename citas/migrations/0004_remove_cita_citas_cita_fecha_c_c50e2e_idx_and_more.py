# Generated by Django 5.1.1 on 2025-01-19 22:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas', '0003_remove_medico_especialidad_citasmedicoespecialidad_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='cita',
            name='citas_cita_fecha_c_c50e2e_idx',
        ),
        migrations.RemoveIndex(
            model_name='horariomedico',
            name='citas_horar_fecha_72b5b3_idx',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='fecha_cita',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='hora_cita',
        ),
        migrations.AddField(
            model_name='cita',
            name='horario_medico',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='citas.horariomedico'),
        ),
    ]

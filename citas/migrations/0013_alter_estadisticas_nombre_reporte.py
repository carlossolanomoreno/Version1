# Generated by Django 5.1.1 on 2025-01-26 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas', '0012_alter_calificacion_calificacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estadisticas',
            name='nombre_reporte',
            field=models.CharField(default='Estadísticas Generales', max_length=100),
        ),
    ]

from rest_framework.test import APITestCase
from rest_framework import status
from django.test import TestCase
from .models import Usuario, Secretaria, Medico, Paciente, Especialidad, Administrador, HorarioMedico
from django.contrib.auth.models import Group

# Pruebas para el modelo Usuario
class UsuarioTests(TestCase):
    def test_crear_usuario(self):
        """Prueba para verificar que los datos de un usuario se guarden correctamente."""
        user = Usuario.objects.create_user(
            username="testuser",
            correo_electronico="test@test.com",
            tipo_usuario="Paciente",
            password="testpass123",
            nombres="Juan",
            apellidos="Pérez"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.correo_electronico, "test@test.com")
        self.assertEqual(user.tipo_usuario, "Paciente")
        self.assertTrue(user.check_password("testpass123"))

    def test_asignar_roles(self):
        """Prueba para verificar que se asignen roles correctamente a los usuarios."""
        user = Usuario.objects.create_user(
            username="medico1",
            correo_electronico="medico@test.com",
            tipo_usuario="Medico",
            password="medico123"
        )
        grupo_medico, _ = Group.objects.get_or_create(name="Medico")
        user.groups.add(grupo_medico)
        self.assertTrue(user.groups.filter(name="Medico").exists())

    def test_envio_password_telegram(self):
        """Prueba para verificar el envío de contraseñas a través de Telegram."""
        user = Usuario.objects.create_user(
            username="telegramuser",
            correo_electronico="telegram@test.com",
            tipo_usuario="Paciente",
            chat_id="123456789",
            password="telegrampass"
        )
        try:
            user.send_password_to_telegram(password="telegrampass")  # Método que debe implementarse
        except Exception as e:
            self.fail(f"El envío de contraseña falló con la excepción: {e}")


# Pruebas para el modelo Secretaria
class SecretariaTests(APITestCase):
    def setUp(self):
        """Configuración inicial de la prueba."""
        self.secretaria_user = Usuario.objects.create_user(
            username="secretaria1",
            correo_electronico="secretaria@example.com",
            tipo_usuario="Secretaria",
            password="password123"
        )
        self.secretaria = Secretaria.objects.create(usuario=self.secretaria_user)

    def test_agendar_cita(self):
        """Prueba para verificar la funcionalidad de agendar citas."""
        self.client.login(username="secretaria1", password="password123")
        response = self.client.post('/secretaria/agendar-cita/', {
            'especialidad_id': 1,
            'medico_id': 1,
            'paciente_id': 1,
            'fecha': '2024-01-01',
            'hora': '10:00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cancelar_cita(self):
        """Prueba para verificar la funcionalidad de cancelar citas."""
        self.client.login(username="secretaria1", password="password123")
        response = self.client.post('/secretaria/cancelar-cita/', {
            'cita_id': 1
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Pruebas para el modelo Administrador
class AdministradorTests(APITestCase):
    def setUp(self):
        """Configuración inicial de la prueba."""
        self.admin_user = Usuario.objects.create_user(
            username="admin1",
            correo_electronico="admin@example.com",
            tipo_usuario="Administrador",
            password="admin123"
        )
        Administrador.objects.create(usuario=self.admin_user)

    def test_generar_reporte(self):
        """Prueba para verificar la generación de reportes."""
        self.client.login(username="admin1", password="admin123")
        response = self.client.get('/administrador/generar-reporte/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gestionar_horario_medico(self):
        """Prueba para verificar la gestión de horarios médicos."""
        self.client.login(username="admin1", password="admin123")
        response = self.client.post('/administrador/gestionar-horario-medico/', {
            "medico": 1,
            "dia": "Lunes",
            "fecha": "2024-01-01",
            "hora_inicio": "09:00:00",
            "hora_fin": "17:00:00",
            "estado": "Disponible"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_supervisar_calificaciones(self):
        """Prueba para verificar la supervisión de calificaciones."""
        self.client.login(username="admin1", password="admin123")
        response = self.client.get('/administrador/supervisar-calificaciones/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

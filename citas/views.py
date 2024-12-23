from django.shortcuts import render, redirect
from .forms import RecuperarCredencialesForm
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password  # Para encriptar contraseñas
from .models import Usuario 
from django.contrib import messages
from django.utils.crypto import get_random_string
from .forms import UsuarioForm, PacienteForm, CitaForm, DiagnosticoForm, RecetaMedicaForm, CalificacionForm
import requests



def login_view(request):
    return render(request, 'login.html')

def recuperar_credenciales(request):
    if request.method == 'POST':
        form = RecuperarCredencialesForm(request.POST)
        if form.is_valid():
            # Procesar la información del formulario (enviar un correo, etc.)
            return HttpResponse("Credenciales enviadas.")
    else:
        form = RecuperarCredencialesForm()
    
    return render(request, 'recuperar_credenciales.html', {'form': form})

def home(request):
    return render(request, 'index.html')
#Telegram
TELEGRAM_BOT_TOKEN = '7093012736:AAGS8s1eyorkNMY9YdV-if4g1raox8HjEzQ'
TELEGRAM_CHAT_ID = '6285348463'

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot7093012736:AAGS8s1eyorkNMY9YdV-if4g1raox8HjEzQ/sendMessage"
    datos = {
        'chat_id': 6285348463,
        'text': mensaje
    }
    try:
        respuesta = requests.post(url, data=datos)
        if respuesta.status_code != 200:
            print(f"Error al enviar mensaje: {respuesta.text}")
    except Exception as e:
        print(f"Excepción al enviar mensaje: {e}")


def notificar_telegram(request):
    mensaje = "Hola, este es un mensaje de prueba desde Django."
    enviar_mensaje_telegram(mensaje)
    return HttpResponse("Mensaje enviado a Telegram.")






def registrar_usuario(request):
    if request.method == 'POST':
        # Recoge los datos del formulario
        cedula = request.POST.get('cedula')
        apellidos = request.POST.get('apellidos')
        nombres = request.POST.get('nombres')
        correo_electronico = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad_residencia = request.POST.get('ciudad de residencia')
        fecha_nacimiento = request.POST.get('fecha de nacimiento')
        genero = request.POST.get('genero')
        username = request.POST.get('usuario')

        # Validación básica (puedes añadir más validaciones según tu lógica)
        if not cedula or not nombres or not apellidos or not correo_electronico:
            messages.error(request, 'Todos los campos obligatorios deben ser llenados.')
            return render(request, 'usuario_registro.html')

        # Genera una contraseña aleatoria
        password = get_random_string(length=8)
        
        # Crea una instancia del modelo Usuario
        try:
            usuario = Usuario.objects.create_user(
                cedula=cedula,
                apellidos=apellidos,
                nombres=nombres,
                correo_electronico=correo_electronico,
                telefono=telefono,
                direccion=direccion,
                ciudad_residencia=ciudad_residencia,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                username=username,
                password=password,  # Asigna la contraseña generada
            )
            # Enviar correo con la contraseña temporal
            send_mail(
                'Contraseña Temporal',
                f'Hola {nombres}, tu contraseña temporal es: {password}. Por favor cámbiala después de iniciar sesión.',
                'noreply@miapp.com',  # Cambia por tu correo configurado
                [correo_electronico],
                fail_silently=False,
            )

            messages.success(request, 'El usuario ha sido registrado exitosamente. Se ha enviado una contraseña temporal al correo.')
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {str(e)}')
    return render(request, 'usuario_registro.html')

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'listar_usuarios.html', {'usuarios': usuarios})

send_mail(
    'Prueba de Envío de Correo',
    'Este es un correo de prueba desde el shell de Django.',
    'noreply@miapp.com',  # Cambia por tu correo configurado
    ['destinatario@ejemplo.com'],  # Cambia por la dirección del destinatario
    fail_silently=False,
)  






def registrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')  # Cambiar por la ruta de tu preferencia
    else:
        form = PacienteForm()
    return render(request, 'pacientes/registro.html', {'form': form})

from .forms import CitaForm

def agendar_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_citas')  # Ruta para mostrar citas
    else:
        form = CitaForm()
    return render(request, 'citas/agendar.html', {'form': form})

def listar_citas(request):
    if request.user.groups.filter(name='Paciente').exists():
        citas = Cita.objects.filter(paciente=request.user.paciente)
    elif request.user.groups.filter(name='Medico').exists():
        citas = Cita.objects.filter(medico__usuario=request.user)
    else:
        citas = Cita.objects.all()
    return render(request, 'citas/lista.html', {'citas': citas})

def registrar_diagnostico(request, cita_id):
    cita = Cita.objects.get(id=cita_id)
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            diagnostico = form.save(commit=False)
            diagnostico.cita = cita
            diagnostico.medico = cita.medico
            diagnostico.save()
            return redirect('detalle_cita', cita_id=cita.id)
    else:
        form = DiagnosticoForm()
    return render(request, 'diagnosticos/registro.html', {'form': form, 'cita': cita})

def emitir_receta(request, cita_id):
    cita = Cita.objects.get(id=cita_id)
    if request.method == 'POST':
        form = RecetaMedicaForm(request.POST)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.cita = cita
            receta.save()
            return redirect('detalle_cita', cita_id=cita.id)
    else:
        form = RecetaMedicaForm()
    return render(request, 'recetas/emitir.html', {'form': form, 'cita': cita})

def registrar_calificacion(request, cita_id):
    cita = Cita.objects.get(id=cita_id)
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.cita = cita
            calificacion.save()
            return redirect('detalle_cita', cita_id=cita.id)
    else:
        form = CalificacionForm()
    return render(request, 'calificaciones/registro.html', {'form': form, 'cita': cita})
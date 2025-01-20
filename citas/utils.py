from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import requests

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


def validar_contraseña(password):
    try:
        validate_password(password)
        print("Contraseña válida")
    except ValidationError as e:
        print("Errores de validación:", e.messages)
        raise e  # Lanza los errores para que otras partes los manejen
    
import requests

TELEGRAM_BOT_TOKEN = "TU_TOKEN_TELEGRAM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def notificar_por_telegram(chat_id, mensaje):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': mensaje
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise ValueError("Error al enviar notificación por Telegram.")
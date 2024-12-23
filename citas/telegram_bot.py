import telegram
from django.conf import settings

# Inicializa el bot
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)

def enviar_mensaje(chat_id, mensaje):
    """
    Envía un mensaje a un usuario o grupo específico.
    :param chat_id: ID del chat (usuario o grupo).
    :param mensaje: Texto del mensaje.
    """
    bot.send_message(chat_id=chat_id, text=mensaje)

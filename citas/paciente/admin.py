from django.contrib import admin
from .models import Usuario, Paciente, Calificacion, Cita

# Register your models here.
admin.site.register(Paciente)
admin.site.register(Cita)
admin.site.register(Calificacion)




@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'correo_electronico', 'tipo_usuario', 'nombres', 'apellidos')
    search_fields = ('username', 'correo_electronico', 'nombres', 'apellidos')
    list_filter = ('tipo_usuario', 'genero')
    
    
@admin.action(description="Enviar mensaje por Telegram")
def enviar_mensaje(modeladmin, request, queryset):
    for usuario in queryset:
        if usuario.chat_id:
            mensaje = "Este es un mensaje importante de la aplicación."
            enviar_mensaje_telegram(usuario.chat_id, mensaje)
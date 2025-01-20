from functools import wraps
from django.http import HttpResponseForbidden

def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden("No tienes acceso a esta página.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@login_required
@group_required('Pacientes')
def dashboard_paciente(request):
    paciente = get_object_or_404(Paciente, usuario=request.user)
    url_agendar_cita = reverse('agendar_cita')
    return render(request, 'dashboard_paciente.html', {'paciente': paciente, 'url_agendar_cita': url_agendar_cita})

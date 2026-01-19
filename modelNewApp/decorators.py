from django.shortcuts import redirect
from django.contrib import messages

def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect("modelNewApp:login")

        if not hasattr(user, "persona"):
            messages.error(request, "No tienes permisos para acceder.")
            return redirect("modelNewApp:control")

        empleado = getattr(user.persona, "empleado", None)

        if not empleado or not empleado.roles.filter(nombre_rol="Administrador").exists():
            messages.error(request, "No tienes permisos para acceder al Dashboard.")
            return redirect("modelNewApp:control")

        return view_func(request, *args, **kwargs)

    return wrapper


# --------------------------------------------------------------
#     USUARIO ES ADMIN?
# --------------------------------------------------------------

def usuario_es_admin(request):
    es_admin = False

    user = request.user
    if user.is_authenticated and hasattr(user, "persona"):
        empleado = getattr(user.persona, "empleado", None)
        if empleado:
            es_admin = empleado.roles.filter(nombre_rol="Administrador").exists()

    return {
        "es_admin": es_admin
    }

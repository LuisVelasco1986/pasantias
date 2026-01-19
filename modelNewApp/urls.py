from django.urls import path
from .views import *

app_name = "modelNewApp"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("recuperar_contraseña/", recuperar_contraseña, name="recuperar_contraseña"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('cambiar_password/', cambiar_password, name='cambiar_password'),
    path("control/", control, name="control"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/personas/", empleados, name="empleados"),
    path("dashboard/personas/agregar", empleados_agregar, name="empleados_agregar"),
    path("dashboard/personas/detalles/<int:id>/", empleados_detalles, name="empleados_detalles"),
    path("dashboard/personas/eliminar/<int:id>/", empleados_eliminar, name="empleados_eliminar"),
    path("dashboard/personas/editar/<int:id>/", empleados_editar, name="empleados_editar"),
    path("dashboard/personas/activar/<int:id>/", empleados_activar, name="empleados_activar"),
    path("dashboard/personas/desactivar/<int:id>/", empleados_desactivar, name="empleados_desactivar"),
    path("dashboard/estadisticos/", estadisticos, name="estadisticos"),
    path("dashboard/control/", dashboard_control, name="dashboard_control"),
    path("dashboard/reportes/", reportes, name="reportes"),
    path("dashboard/perfil/", perfil, name="perfil"),
    path("buscar-persona/", buscar_persona_por_cedula, name="buscar_persona"),
    path('persona/<int:persona_id>/export_pdf/', exportar_historial_pdf, name='exportar_pdf'),
    path('persona/<int:persona_id>/export_excel/', exportar_historial_excel, name='exportar_excel'),
    path("reportes/pdf/", exportar_pdf, name="exportar_pdf"),
]
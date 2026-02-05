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
    path("control/pie", control_pie, name="control_pie"),
    path("control/vehiculo", control_vehiculo, name="control_vehiculo"),
    path("ajax/buscar-vehiculo/", buscar_vehiculo_por_placa, name="buscar_vehiculo"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/personas/", empleados, name="empleados"),
    path("dashboard/personas/agregar", empleados_agregar, name="empleados_agregar"),
    path("dashboard/personas/detalles/<int:id>/", empleados_detalles, name="empleados_detalles"),
    path("dashboard/personas/eliminar/<int:id>/", empleados_eliminar, name="empleados_eliminar"),
    path("dashboard/personas/editar/<int:id>/", empleados_editar, name="empleados_editar"),
    path("dashboard/personas/activar/<int:id>/", empleados_activar, name="empleados_activar"),
    path("dashboard/personas/desactivar/<int:id>/", empleados_desactivar, name="empleados_desactivar"),
    path("dashboard/vehiculos/", vehiculos, name="vehiculos"),
    path("dashboard/vehiculos/agregar", vehiculos_agregar, name="vehiculos_agregar"),
    path("dashboard/vehiculos/detalles/<int:id>/", vehiculos_detalles, name="vehiculos_detalles"),
    path("dashboard/vehiculos/eliminar/<int:id>/", vehiculos_eliminar, name="vehiculos_eliminar"),
    path("dashboard/vehiculos/editar/<int:id>/", vehiculos_editar, name="vehiculos_editar"),
    path("dashboard/estadisticos/", estadisticos, name="estadisticos"),
    path("dashboard/control/", dashboard_control, name="dashboard_control"),
    path("dashboard/reportes/", reportes, name="reportes"),
    path("dashboard/perfil/", perfil, name="perfil"),
    path("buscar-persona/", buscar_persona_por_cedula, name="buscar_persona"),
    path('persona/<int:persona_id>/export_pdf/', exportar_historial_pdf, name='exportar_pdf'),
    path('vehiculos/<int:vehiculo_id>/export_pdf/', exportar_historial_pdf_vehiculos, name='exportar_pdf_vehiculo'),
    path('persona/<int:persona_id>/export_excel/', exportar_historial_excel, name='exportar_excel'),
    path('vehiculos/<int:vehiculo_id>/export_excel/', exportar_historial_excel_vehiculos, name='exportar_excel_vehiculo'),
    path("reportes/pdf/", exportar_pdf, name="exportar_pdf"),
]
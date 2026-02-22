from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, user_logged_in
from django.contrib.auth.decorators import login_required
import secrets
from django.core.mail import send_mail
from django.db.models import Q, Max, Count, F, IntegerField

from django.db.models.functions import Cast, TruncDate, TruncDay, TruncWeek, TruncMonth, TruncHour, ExtractHour

import datetime
from datetime import datetime, date

from django.utils import timezone
from django.utils.timezone import now, timedelta, localdate, make_aware

from django.http import JsonResponse
from .models import Persona

from django.core.paginator import Paginator

from modelNewApp.models import *
from modelNewApp.decorators import solo_admin

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse

from reportlab.pdfbase.pdfmetrics import stringWidth

import csv


class HomeView(View):
    def get(self, request):
        return render(request, "pages/index.html")


def login_view(request):
    if user_logged_in == True:
        return redirect("modelNewApp:control")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.debe_cambiar_password:
                return redirect('modelNewApp:cambiar_password')
            return redirect("modelNewApp:control")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            # print("Correo o contraseña incorrectos")
            return redirect("modelNewApp:home")

    return redirect("modelNewApp:home")


def logout_view(request):
    logout(request)
    return redirect('modelNewApp:home')


@login_required
def cambiar_password(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            request.user.set_password(password1)
            request.user.debe_cambiar_password = False
            request.user.save()
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('modelNewApp:home')

    return render(request, 'pages/cambiar_password.html')


@login_required
def control(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo_ingreso")

        if tipo == "PIE":
            return redirect("modelNewApp:control_pie")
        elif tipo == "VEHICULO":
            return redirect("modelNewApp:control_vehiculo")

    return render(request, "pages/control.html")


@login_required
def control_pie(request):
    departamentos = Departamento.objects.all().order_by('nombre')
    dict = {"departamentos": departamentos}
    if request.method == "POST":
        if "forzar_salida" in request.POST:
            print("Forzar salida")
            print(request.POST.get("motivo_forzar_salida"))
            print(request.POST.get("visitante"))

            if request.POST.get("visitante"):
                print(request.POST.get("cedula_visitante"))
                if Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).exists():
                    print("El visitante existe")
                    if RegistroAcceso.objects.filter(id_persona=Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()).last() and RegistroAcceso.objects.filter(id_persona=Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()).last().tipo_movimiento == "INGRESO":
                        print("El ultimo fué ingreso")
                        registro = RegistroAcceso()
                        registro.id_persona = Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()
                        registro.fecha_hora = datetime.now()
                        registro.tipo_movimiento = "EGRESO"
                        registro.observacion = request.POST.get("motivo_forzar_salida")
                        registro.save()
                        dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos}
                    else:
                        print("El último fué egreso")
                        dict = {"mensaje_error": "El visitante no se encuentra dentro del edificio.",
                                "departamentos": departamentos}
                else:
                    print("El visitante no existe")
                    dict = {"mensaje_error": "No existe un visitante con esa cédula", "departamentos": departamentos}
            else:
                print(request.POST.get("codigo"))
                if Persona.objects.filter(codigo_p00=request.POST.get("codigo")).exists():
                    print("La persona existe")
                    if RegistroAcceso.objects.filter(id_persona=Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()).last() and RegistroAcceso.objects.filter(id_persona=Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()).last().tipo_movimiento == "INGRESO":
                        print("El ultimo fué ingreso")
                        registro = RegistroAcceso()
                        registro.id_persona = Persona.objects.filter(
                        codigo_p00=request.POST.get("codigo")).first()
                        registro.fecha_hora = datetime.now()
                        registro.tipo_movimiento = "EGRESO"
                        registro.observacion = request.POST.get("motivo_forzar_salida")
                        registro.save()
                        dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos}
                    else:
                        print("El último fué egreso")
                        dict = {"mensaje_error": "El empleado no se encuentra dentro del edificio.",
                                "departamentos": departamentos}
                else:
                    print("La persona no existe")
                    dict = {"mensaje_error": "No existe un empleado con ese código", "departamentos": departamentos}

        else:
            print(request.POST.get("departamento"))
            departamentos = Departamento.objects.all().order_by('nombre')
            if request.POST.get("visitante"):
                visitante = Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()
                if visitante:
                    registro_abierto = RegistroAcceso.objects.filter(id_persona=visitante).last()
                    if registro_abierto and registro_abierto.tipo_movimiento == "INGRESO":
                        if request.POST.get("ingreso"):
                            dict = {
                                "mensaje_error": "No puede registrar ingreso porque tiene un registro abierto actualmente.",
                                "departamentos": departamentos}
                        else:
                            if request.POST.get("nombre_visitante") != visitante.nombres:
                                visitante.nombres = request.POST.get("nombre_visitante")
                                visitante.save()
                            if request.POST.get("apellido_visitante") != visitante.apellidos:
                                visitante.apellidos = request.POST.get("apellido_visitante")
                                visitante.save()
                            registro_abierto = RegistroAcceso()
                            registro_abierto.id_persona = visitante
                            registro_abierto.fecha_hora = datetime.now()
                            registro_abierto.tipo_movimiento = "EGRESO"
                            registro_abierto.save()
                            dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos}
                    else:
                        if request.POST.get("ingreso"):
                            registro = RegistroAcceso()
                            registro.id_persona = visitante
                            if request.POST.get("nombre_visitante") != visitante.nombres:
                                visitante.nombres = request.POST.get("nombre_visitante")
                                visitante.save()
                            if request.POST.get("apellido_visitante") != visitante.apellidos:
                                visitante.apellidos = request.POST.get("apellido_visitante")
                                visitante.save()
                            registro.tipo_movimiento = "INGRESO"
                            if request.POST.get("departamento"):
                                registro.departamento_destino = Departamento.objects.filter(
                                    nombre=request.POST.get("departamento")).first()
                            else:
                                dict = {"mensaje_error": "Debe seleccionar un departamento.",
                                        "departamentos": departamentos}
                                return render(request, "pages/control_pie.html", dict)
                            # registro.departamento_destino =
                            registro.fecha_hora = datetime.now()
                            registro.save()
                            dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos}
                        else:
                            dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                    "departamentos": departamentos}
                else:
                    if request.POST.get("ingreso"):
                        empleado = Persona()
                        empleado.id_tipo = TipoEmpleado.objects.get(nombre_tipo="Visitante")
                        empleado.nombres = request.POST.get("nombre_visitante")
                        empleado.apellidos = request.POST.get("apellido_visitante")
                        empleado.cedula = request.POST.get("cedula_visitante")
                        empleado.save()

                        registro = RegistroAcceso()
                        registro.id_persona = empleado
                        registro.tipo_movimiento = "INGRESO"
                        if request.POST.get("departamento"):
                            registro.departamento_destino = Departamento.objects.filter(
                                nombre=request.POST.get("departamento")).first()
                        else:
                            dict = {"mensaje_error": "Debe seleccionar un departamento.",
                                    "departamentos": departamentos}
                            return render(request, "pages/control_pie.html", dict)
                        # registro.departamento_destino =
                        registro.fecha_hora = datetime.now()
                        registro.save()
                        dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos}
                    else:
                        dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                "departamentos": departamentos}
            else:
                empleado = Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()
                if empleado:
                    registro_abierto = RegistroAcceso.objects.filter(id_persona=empleado).last()
                    if registro_abierto and registro_abierto.tipo_movimiento == "INGRESO":
                        if request.POST.get("ingreso"):
                            dict = {
                                "mensaje_error": "No puede registrar ingreso porque tiene un registro abierto actualmente.",
                                "departamentos": departamentos}
                        else:
                            registro_abierto = RegistroAcceso()
                            registro_abierto.id_persona = empleado
                            registro_abierto.fecha_hora = datetime.now()
                            registro_abierto.tipo_movimiento = "EGRESO"
                            registro_abierto.save()
                            dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos}
                    else:
                        if request.POST.get("ingreso"):
                            registro = RegistroAcceso()
                            registro.id_persona = empleado
                            registro.tipo_movimiento = "INGRESO"
                            registro.departamento_destino = empleado.departamento
                            registro.fecha_hora = datetime.now()
                            registro.save()
                            dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos}
                        else:
                            dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                    "departamentos": departamentos}
                else:
                    dict = {"mensaje_error": "No existe un empleado con ese código", "departamentos": departamentos}
    return render(request, "pages/control_pie.html", dict)


@login_required
def control_vehiculo(request):
    departamentos = Departamento.objects.all().order_by('nombre')
    marcas = Marca.objects.all().order_by('nombre')
    modelos = Modelo.objects.all().order_by('nombre')
    dict = {"departamentos": departamentos, "marcas": marcas, "modelos": modelos}
    if request.method == "POST":
        marcas = Marca.objects.all().order_by('nombre')
        modelos = Modelo.objects.all().order_by('nombre')
        marca_txt = request.POST.get("marca").strip()
        modelo_txt = request.POST.get("modelo").strip()

        marca, _ = Marca.objects.get_or_create(
            nombre__iexact=marca_txt,
            defaults={"nombre": marca_txt}
        )

        modelo, _ = Modelo.objects.get_or_create(
            nombre__iexact=modelo_txt,
            marca=marca,
            defaults={
                "nombre": modelo_txt,
                "marca": marca
            }
        )
        if "forzar_salida" in request.POST:
            print("Forzar salida")
            print(request.POST.get("motivo_forzar_salida"))
            print(request.POST.get("visitante"))

            if request.POST.get("visitante"):
                print(request.POST.get("cedula_visitante"))
                if Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).exists():
                    print("El visitante existe")
                    if RegistroAcceso.objects.filter(
                            id_persona=Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()).last() and RegistroAcceso.objects.filter(
                            id_persona=Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()).last().tipo_movimiento == "INGRESO":
                        print("El ultimo fué ingreso")

                        # ------------------------------------------------
                        # Creo registro
                        # ------------------------------------------------
                        registro = RegistroAcceso()
                        registro.id_persona = Persona.objects.filter(
                        cedula=request.POST.get("cedula_visitante")).first()
                        registro.fecha_hora = datetime.now()
                        registro.tipo_movimiento = "EGRESO"
                        # ------------------------------------------------
                        # Checkeo vehiculo
                        # ------------------------------------------------
                        vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                        if vehiculo:
                            vehiculo.marca = marca
                            vehiculo.modelo = modelo
                            if request.POST.get("codigo_vehiculo"):
                                vehiculo.codigo = request.POST.get("codigo_vehiculo")
                            vehiculo.save()
                        else:
                            vehiculo = Vehiculo()
                            vehiculo.placa = request.POST.get("placa")
                            vehiculo.marca = marca
                            vehiculo.modelo = modelo
                            if request.POST.get("codigo_vehiculo"):
                                vehiculo.codigo = request.POST.get("codigo_vehiculo")
                            vehiculo.save()
                        registro.vehiculo = vehiculo
                        registro.observacion = request.POST.get("motivo_forzar_salida")
                        registro.save()
                        dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                    else:
                        print("El último fué egreso")
                        dict = {"mensaje_error": "El visitante no se encuentra dentro del edificio.",
                                "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                else:
                    print("El visitante no existe")
                    dict = {"mensaje_error": "No existe un visitante con esa cédula", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
            else:
                print(request.POST.get("codigo"))
                if Persona.objects.filter(codigo_p00=request.POST.get("codigo")).exists():
                    print("La persona existe")
                    if RegistroAcceso.objects.filter(
                            id_persona=Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()).last() and RegistroAcceso.objects.filter(
                            id_persona=Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()).last().tipo_movimiento == "INGRESO":
                        print("El ultimo fué ingreso")
                        registro = RegistroAcceso()
                        registro.id_persona = Persona.objects.filter(
                        codigo_p00=request.POST.get("codigo")).first()
                        registro.fecha_hora = datetime.now()
                        registro.tipo_movimiento = "EGRESO"
                        # ------------------------------------------------
                        # Checkeo vehiculo
                        # ------------------------------------------------
                        vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                        if vehiculo:
                            vehiculo.marca = marca
                            vehiculo.modelo = modelo
                            if request.POST.get("codigo_vehiculo"):
                                vehiculo.codigo = request.POST.get("codigo_vehiculo")
                            vehiculo.save()
                        else:
                            vehiculo = Vehiculo()
                            vehiculo.placa = request.POST.get("placa")
                            vehiculo.marca = marca
                            vehiculo.modelo = modelo
                            if request.POST.get("codigo_vehiculo"):
                                vehiculo.codigo = request.POST.get("codigo_vehiculo")
                            vehiculo.save()
                        registro.vehiculo = vehiculo
                        registro.observacion = request.POST.get("motivo_forzar_salida")
                        registro.save()
                        dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                    else:
                        print("El último fué egreso")
                        dict = {"mensaje_error": "El empleado no se encuentra dentro del edificio.",
                                "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                else:
                    print("La persona no existe")
                    dict = {"mensaje_error": "No existe un empleado con ese código", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
        else:
            departamentos = Departamento.objects.all().order_by('nombre')
            if request.POST.get("visitante"):
                visitante = Persona.objects.filter(cedula=request.POST.get("cedula_visitante")).first()
                if visitante:
                    registro_abierto = RegistroAcceso.objects.filter(id_persona=visitante).last()
                    if registro_abierto and registro_abierto.tipo_movimiento == "INGRESO":
                        if request.POST.get("ingreso"):
                            dict = {
                                "mensaje_error": "No puede registrar ingreso porque tiene un registro abierto actualmente.",
                                "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                        else:
                            if request.POST.get("nombre_visitante") != visitante.nombres:
                                visitante.nombres = request.POST.get("nombre_visitante")
                                visitante.save()
                            if request.POST.get("apellido_visitante") != visitante.apellidos:
                                visitante.apellidos = request.POST.get("apellido_visitante")
                                visitante.save()
                            registro_abierto = RegistroAcceso()
                            registro_abierto.id_persona = visitante
                            registro_abierto.fecha_hora = datetime.now()
                            registro_abierto.tipo_movimiento = "EGRESO"
                            vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                            if vehiculo:
                                registro_abierto.vehiculo = vehiculo
                            else:
                                vehiculo = Vehiculo()
                                vehiculo.placa = request.POST.get("placa")
                                vehiculo.marca = marca
                                vehiculo.modelo = modelo
                                if request.POST.get("codigo_vehiculo"):
                                    vehiculo.codigo = request.POST.get("codigo_vehiculo")
                                vehiculo.save()
                            registro_abierto.vehiculo = vehiculo
                            registro_abierto.save()
                            dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                    else:
                        if request.POST.get("ingreso"):
                            registro = RegistroAcceso()
                            registro.id_persona = visitante
                            if request.POST.get("nombre_visitante") != visitante.nombres:
                                visitante.nombres = request.POST.get("nombre_visitante")
                                visitante.save()
                            if request.POST.get("apellido_visitante") != visitante.apellidos:
                                visitante.apellidos = request.POST.get("apellido_visitante")
                                visitante.save()
                            registro.tipo_movimiento = "INGRESO"
                            if request.POST.get("departamento"):
                                registro.departamento_destino = Departamento.objects.filter(
                                    nombre=request.POST.get("departamento")).first()
                            else:
                                dict = {"mensaje_error": "Debe seleccionar un departamento.",
                                        "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                                return render(request, "pages/control_vehiculo.html", dict)
                            # registro.departamento_destino =
                            registro.fecha_hora = datetime.now()
                            vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                            if vehiculo:
                                registro.vehiculo = vehiculo
                            else:
                                vehiculo = Vehiculo()
                                vehiculo.placa = request.POST.get("placa")
                                vehiculo.marca = marca
                                vehiculo.modelo = modelo
                                if request.POST.get("codigo_vehiculo"):
                                    vehiculo.codigo = request.POST.get("codigo_vehiculo")
                                vehiculo.save()
                            registro.vehiculo = vehiculo
                            registro.save()
                            dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                        else:
                            dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                    "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                else:
                    if request.POST.get("ingreso"):
                        empleado = Persona()
                        empleado.id_tipo = TipoEmpleado.objects.get(nombre_tipo="Visitante")
                        empleado.nombres = request.POST.get("nombre_visitante")
                        empleado.apellidos = request.POST.get("apellido_visitante")
                        empleado.cedula = request.POST.get("cedula_visitante")
                        empleado.save()

                        registro = RegistroAcceso()
                        registro.id_persona = empleado
                        registro.tipo_movimiento = "INGRESO"
                        if request.POST.get("departamento"):
                            registro.departamento_destino = Departamento.objects.filter(
                                nombre=request.POST.get("departamento")).first()
                        else:
                            dict = {"mensaje_error": "Debe seleccionar un departamento.",
                                    "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                            return render(request, "pages/control_vehiculo.html", dict)
                        # registro.departamento_destino =
                        registro.fecha_hora = datetime.now()
                        vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                        if vehiculo:
                            registro.vehiculo = vehiculo
                        else:
                            vehiculo = Vehiculo()
                            vehiculo.placa = request.POST.get("placa")
                            vehiculo.marca = marca
                            vehiculo.modelo = modelo
                            if request.POST.get("codigo_vehiculo"):
                                vehiculo.codigo = request.POST.get("codigo_vehiculo")
                            vehiculo.save()
                        registro.vehiculo = vehiculo
                        registro.save()
                        dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                    else:
                        dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
            else:
                empleado = Persona.objects.filter(codigo_p00=request.POST.get("codigo")).first()
                if empleado:
                    registro_abierto = RegistroAcceso.objects.filter(id_persona=empleado).last()
                    if registro_abierto and registro_abierto.tipo_movimiento == "INGRESO":
                        if request.POST.get("ingreso"):
                            dict = {
                                "mensaje_error": "No puede registrar ingreso porque tiene un registro abierto actualmente.",
                                "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                        else:
                            registro_abierto = RegistroAcceso()
                            registro_abierto.id_persona = empleado
                            registro_abierto.fecha_hora = datetime.now()
                            registro_abierto.tipo_movimiento = "EGRESO"
                            vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                            if vehiculo:
                                registro_abierto.vehiculo = vehiculo
                            else:
                                vehiculo = Vehiculo()
                                vehiculo.placa = request.POST.get("placa")
                                vehiculo.marca = marca
                                vehiculo.modelo = modelo
                                if request.POST.get("codigo_vehiculo"):
                                    vehiculo.codigo = request.POST.get("codigo_vehiculo")
                                vehiculo.save()
                            registro_abierto.vehiculo = vehiculo
                            registro_abierto.save()
                            dict = {"mensaje": "Ha registrado su salida efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                    else:
                        if request.POST.get("ingreso"):
                            registro = RegistroAcceso()
                            registro.id_persona = empleado
                            registro.tipo_movimiento = "INGRESO"
                            registro.departamento_destino = empleado.departamento
                            registro.fecha_hora = datetime.now()
                            vehiculo = Vehiculo.objects.filter(placa=request.POST.get("placa")).first()
                            if vehiculo:
                                registro.vehiculo = vehiculo
                            else:
                                vehiculo = Vehiculo()
                                vehiculo.placa = request.POST.get("placa")
                                vehiculo.marca = marca
                                vehiculo.modelo = modelo
                                if request.POST.get("codigo_vehiculo"):
                                    vehiculo.codigo = request.POST.get("codigo_vehiculo")
                                vehiculo.save()
                            registro.vehiculo = vehiculo
                            registro.save()
                            dict = {"mensaje": "Ha registrado su entrada efectivamente.", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                        else:
                            dict = {"mensaje_error": "No puede registrar salida porque no tiene registro de entrada.",
                                    "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
                else:
                    dict = {"mensaje_error": "No existe un empleado con ese código", "departamentos": departamentos, "marcas": marcas, "modelos": modelos}
    return render(request, "pages/control_vehiculo.html", dict)


def buscar_persona_por_cedula(request):
    cedula = request.GET.get("cedula")

    if not cedula:
        return JsonResponse({"found": False})

    persona = Persona.objects.filter(cedula=cedula).first()

    if persona:
        return JsonResponse({
            "found": True,
            "nombres": persona.nombres,
            "apellidos": persona.apellidos
        })

    return JsonResponse({"found": False})


def buscar_vehiculo_por_placa(request):
    placa = request.GET.get("placa")

    try:
        vehiculo = Vehiculo.objects.get(placa__iexact=placa)
        return JsonResponse({
            "existe": True,
            "marca": vehiculo.marca.nombre,
            "modelo": vehiculo.modelo.nombre,
            "codigo": vehiculo.codigo,
        })
    except Vehiculo.DoesNotExist:
        return JsonResponse({"existe": False})


@solo_admin
@login_required
def dashboard(request):
    today = timezone.localdate()

    # ─────────────────────────────────────────────
    # Gráfica: Ingresos últimos 7 días
    # ─────────────────────────────────────────────
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    ingresos_por_dia = []
    for day in last_7_days:
        count = RegistroAcceso.objects.filter(
            tipo_movimiento='INGRESO',
            fecha_hora__date=day
        ).count()

        ingresos_por_dia.append({
            'fecha': day.strftime('%d/%m'),
            'cantidad': count
        })

    # ─────────────────────────────────────────────
    # Personas dentro del edificio
    # (último movimiento = INGRESO)
    # ─────────────────────────────────────────────
    ultimos_movimientos = (
        RegistroAcceso.objects
        .values('id_persona')
        .annotate(ultima_fecha=Max('fecha_hora'))
    )

    dentro_ids = []

    for mov in ultimos_movimientos:
        ultimo = RegistroAcceso.objects.get(
            id_persona_id=mov['id_persona'],
            fecha_hora=mov['ultima_fecha']
        )
        if ultimo.tipo_movimiento == 'INGRESO':
            dentro_ids.append(ultimo.id)

    dentro = RegistroAcceso.objects.filter(id__in=dentro_ids).order_by("fecha_hora")

    # ─────────────────────────────────────────────
    # Ingresos y salidas de HOY
    # ─────────────────────────────────────────────
    ingresos = RegistroAcceso.objects.filter(
        tipo_movimiento='INGRESO',
        fecha_hora__date=today
    )

    salidas = RegistroAcceso.objects.filter(
        tipo_movimiento='EGRESO',
        fecha_hora__date=today
    )

    # ─────────────────────────────────────────────
    # Total personas
    # ─────────────────────────────────────────────
    total = Persona.objects.count()

    context = {
        "dentro": dentro,
        "total": total,
        "ingresos": ingresos,
        "salidas": salidas,
        "ingresos_por_dia": ingresos_por_dia,
    }

    return render(request, "pages/dashboard_main.html", context)


@solo_admin
@login_required
def empleados(request):
    empleados = Persona.objects.all().order_by("nombres")
    tipos = TipoEmpleado.objects.all().order_by("nombre_tipo")

    search = request.GET.get('search', '')
    estado = request.GET.get('estado')
    tipo_id = request.GET.get('tipo')
    orden = request.GET.get('orden')

    if search:
        empleados = empleados.filter(
            Q(nombres__icontains=search) |
            Q(apellidos__icontains=search) |
            Q(codigo_p00__icontains=search)
        )

    tipo_seleccionado = None
    if tipo_id:
        tipo_seleccionado = TipoEmpleado.objects.get(id=tipo_id).nombre_tipo

    if estado == 'activo':
        empleados = empleados.filter(activo=True)
    elif estado == 'inactivo':
        empleados = empleados.filter(activo=False)

    if tipo_id:
        empleados = empleados.filter(id_tipo_id=tipo_id)

    if orden == "nombre":
        empleados = empleados.order_by("nombres", "apellidos")
    elif orden == "-nombre":
        empleados = empleados.order_by("-nombres", "-apellidos")
    elif orden == "fecha":
        empleados = empleados.order_by("fecha_registro")
    elif orden == "-fecha":
        empleados = empleados.order_by("-fecha_registro")
    elif orden == "codigo":
        empleados = empleados.order_by("codigo_p00")
    elif orden == "-codigo":
        empleados = empleados.order_by("-codigo_p00")
    elif orden == "-estado":
        empleados = empleados.order_by("-activo")
    elif orden == "estado":
        empleados = empleados.order_by("activo")
    else:
        empleados = empleados.order_by("nombres")

    # Si quiero arreglar por código numérico --------------------------------
    # elif orden == "codigo":
    #     empleados = empleados.annotate(
    #         codigo_num=Cast("codigo_p00", IntegerField())
    #     ).order_by("codigo_num")
    # -----------------------------------------------------------------------

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/personas_list.html', {
            'empleados': empleados,
            "tipos": tipos,
            "tipo_seleccionado": tipo_seleccionado,
            "orden_actual": orden
        })

    dict = {"empleados": empleados, "tipos": tipos, "tipo_seleccionado": tipo_seleccionado, "orden_actual": orden}

    return render(request, "pages/empleados.html", dict)


@solo_admin
@login_required
def empleados_agregar(request):
    if request.POST:
        sexo = request.POST.get('sexo')
        tipos = TipoEmpleado.objects.all().order_by('nombre_tipo').exclude(nombre_tipo="Visitante")
        roles_ids = request.POST.getlist('roles')
        es_admin = Rol.objects.filter(
            id__in=roles_ids,
            nombre_rol__iexact="Administrador"
        ).exists()
        departamentos = Departamento.objects.all().order_by("nombre")

        if not sexo:
            messages.error(request, "Debe seleccionar un sexo.")
            roles = Rol.objects.all().order_by('nombre_rol')
            dict = {"error": "Debe seleccionar un sexo", "data": request.POST, "tipos": tipos, "roles": roles,
                    "departamentos": departamentos}
            return render(request, "pages/empleados_agregar.html", dict)
        else:
            if request.POST.get("administrador"):
                if roles_ids:

                    empleado = Persona()
                    empleado.nombres = request.POST.get('nombres')
                    empleado.apellidos = request.POST.get('apellidos')
                    if Persona.objects.filter(cedula=request.POST.get('cedula')).exists():
                        messages.error(request, "Ya existe un empleado con esa cédula.")
                        return render(
                            request,
                            "pages/empleados_agregar.html",
                            {
                                "error": "Ya existe un empleado con esa cédula.",
                                "data": request.POST,
                                "roles": Rol.objects.all(),
                                "tipos": TipoEmpleado.objects.all().exclude(nombre_tipo="Visitante"),
                                "departamentos": departamentos,
                            })
                    else:
                        empleado.cedula = request.POST.get('cedula')
                    if Persona.objects.filter(codigo_p00=request.POST.get('codigo')).exists():
                        messages.error(request, "Ya existe un empleado con ése código P00.")
                        return render(
                            request,
                            "pages/empleados_agregar.html",
                            {
                                "error": "Ya existe un empleado con ése código P00.",
                                "data": request.POST,
                                "roles": Rol.objects.all(),
                                "tipos": TipoEmpleado.objects.all().exclude(nombre_tipo="Visitante"),
                                "departamentos": departamentos,
                            })
                    else:
                        empleado.codigo_p00 = request.POST.get('codigo')
                    if request.POST.get('departamento'):
                        empleado.departamento = Departamento.objects.filter(id=request.POST.get('departamento')).first()
                    else:
                        empleado.departamento = None
                    empleado.sexo = request.POST.get('sexo')
                    empleado.id_tipo = TipoEmpleado.objects.get(id=request.POST.get('tipo_persona'))
                    if 'foto_perfil' in request.FILES:
                        empleado.foto_perfil = request.FILES['foto_perfil']
                    empleado.save()

                    usuario = Usuario()
                    usuario.email = request.POST.get('email')
                    usuario.username = request.POST.get('email')
                    usuario.first_name = request.POST.get('nombres')
                    usuario.last_name = request.POST.get('apellidos')
                    usuario.persona = empleado
                    password_temporal = secrets.token_urlsafe(8)
                    usuario.set_password(password_temporal)
                    usuario.debe_cambiar_password = True
                    # 👉 permisos admin
                    usuario.is_staff = True  # puede entrar al admin
                    usuario.is_active = True  # usuario activo
                    usuario.is_superuser = es_admin
                    usuario.save()
                    usuario.roles.set(roles_ids)

                    send_mail(
                        'Acceso al sistema',
                        f'''
                    Hola {usuario.first_name},

                    Se ha creado una cuenta para ti.

                    Usuario: {usuario.email}
                    Contraseña temporal: {password_temporal}

                    Por seguridad deberás cambiar esta contraseña al iniciar sesión.
                    ''',
                        'no-reply@sistema.com',
                        [usuario.email],
                        fail_silently=False,
                    )

                else:
                    messages.error(request, "Debe seleccionar al menos un rol.")
                    roles = Rol.objects.all().order_by('nombre_rol')
                    dict = {"error": "Debe seleccionar al menos un rol.", "data": request.POST, "tipos": tipos,
                            "roles": roles, "departamentos": departamentos}
                    return render(request, "pages/empleados_agregar.html", dict)
            else:
                empleado = Persona()
                empleado.nombres = request.POST.get('nombres')
                empleado.apellidos = request.POST.get('apellidos')
                empleado.cedula = request.POST.get('cedula')
                empleado.codigo_p00 = request.POST.get('codigo')
                if request.POST.get('departamento'):
                    empleado.departamento = Departamento.objects.filter(id=request.POST.get('departamento')).first()
                else:
                    empleado.departamento = None
                empleado.sexo = request.POST.get('sexo')
                empleado.id_tipo = TipoEmpleado.objects.get(id=request.POST.get('tipo_persona'))
                if 'foto_perfil' in request.FILES:
                    empleado.foto_perfil = request.FILES['foto_perfil']
                empleado.save()

            return redirect("modelNewApp:empleados")

    tipos = TipoEmpleado.objects.all().order_by('nombre_tipo').exclude(nombre_tipo="Visitante")
    roles = Rol.objects.all().order_by('nombre_rol')
    departamentos = Departamento.objects.all().order_by("nombre")
    dict = {"tipos": tipos, "roles": roles, "departamentos": departamentos}
    return render(request, "pages/empleados_agregar.html", dict)


@solo_admin
@login_required
def empleados_detalles(request, id):
    persona = get_object_or_404(Persona, id=id)

    historial_accesos = (
        RegistroAcceso.objects
        .filter(id_persona=persona)
        .select_related('departamento_destino')
        .order_by('-fecha_hora')
    )

    # ──────────────── Paginación ────────────────
    paginator = Paginator(historial_accesos, 20)  # 10 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    dict = {"persona": persona, "page_obj": page_obj, }
    return render(request, "pages/empleados_detalles.html", dict)


@solo_admin
@login_required
def empleados_eliminar(request, id):
    persona = get_object_or_404(Persona, id=id)

    if hasattr(persona, 'empleado') and persona.empleado:
        persona.empleado.delete()

    persona.delete()
    return redirect("modelNewApp:empleados")


@solo_admin
@login_required
def empleados_editar(request, id):
    persona = get_object_or_404(Persona, id=id)

    roles_persona = []
    if persona and hasattr(persona, 'empleado'):
        usuario = persona.empleado
        roles_persona = usuario.roles.values_list('id', flat=True)

    if request.POST:
        sexo = request.POST.get('sexo')
        tipos = TipoEmpleado.objects.all().order_by('nombre_tipo')
        roles_ids = request.POST.getlist('roles')
        es_admin = Rol.objects.filter(
            id__in=roles_ids,
            nombre_rol__iexact="Administrador"
        ).exists()
        departamentos = Departamento.objects.all().order_by("nombre")

        persona = get_object_or_404(Persona, id=id)

        roles_persona = []
        usuario = False
        if persona and hasattr(persona, 'empleado'):
            usuario = persona.empleado
            roles_persona = usuario.roles.values_list('id', flat=True)

        if not sexo:
            messages.error(request, "Debe seleccionar un sexo.")
            dict = {"error": "Debe seleccionar un sexo", "data": request.POST, "tipos": tipos, "persona": persona,
                    "departamentos": departamentos}
            return render(request, "pages/empleados_editar.html", dict)
        else:
            persona.nombres = request.POST.get('nombres')
            persona.apellidos = request.POST.get('apellidos')
            if Persona.objects.filter(cedula=request.POST.get('cedula')).exclude(id=persona.id).exists():
                messages.error(request, "Ya existe un empleado con esa cédula.")
                return render(
                    request,
                    "pages/empleados_editar.html",
                    {
                        "error": "Ya existe un empleado con esa cédula.",
                        "data": request.POST,
                        "roles": Rol.objects.all(),
                        "tipos": TipoEmpleado.objects.all().exclude(id=2),
                        "persona": persona,
                        "roles_persona": roles_persona,
                        "departamentos": departamentos,
                    })
            else:
                persona.cedula = request.POST.get('cedula')
            if Persona.objects.filter(codigo_p00=request.POST.get('codigo')).exclude(id=persona.id).exists():
                messages.error(request, "Ya existe un empleado con ése código P00.")
                return render(
                    request,
                    "pages/empleados_editar.html",
                    {
                        "error": "Ya existe un empleado con ése código P00.",
                        "data": request.POST,
                        "roles": Rol.objects.all(),
                        "tipos": TipoEmpleado.objects.all().exclude(id=2),
                        "persona": persona,
                        "roles_persona": roles_persona,
                        "departamentos": departamentos,
                    })
            else:
                persona.codigo_p00 = request.POST.get('codigo')
            if request.POST.get('departamento'):
                persona.departamento = Departamento.objects.filter(id=request.POST.get('departamento')).first()
            else:
                persona.departamento = None
            persona.sexo = request.POST.get('sexo')
            persona.id_tipo = TipoEmpleado.objects.get(id=request.POST.get('tipo_persona'))
            if 'foto_perfil' in request.FILES:
                persona.foto_perfil = request.FILES['foto_perfil']
            persona.save()

            if request.POST.get("administrador"):
                if roles_ids:

                    if usuario:

                        usuario.username = request.POST.get('email')
                        usuario.first_name = request.POST.get('nombres')
                        usuario.last_name = request.POST.get('apellidos')
                        usuario.persona = persona
                        # 👉 permisos admin
                        usuario.is_staff = True  # puede entrar al admin
                        usuario.is_active = True  # usuario activo
                        usuario.is_superuser = es_admin
                        usuario.save()
                        usuario.roles.set(roles_ids)

                        if request.POST.get('email') != usuario.email:
                            password_temporal = secrets.token_urlsafe(8)
                            usuario.set_password(password_temporal)
                            usuario.debe_cambiar_password = True
                            usuario.email = request.POST.get('email')
                            usuario.username = request.POST.get('email')
                            usuario.save()
                            send_mail(
                                'Acceso al sistema',
                                f'''
                                    Hola {usuario.first_name},

                                    Se ha cambiar su dirección de correo electrónico.

                                    Usuario: {usuario.email}
                                    Contraseña temporal: {password_temporal}

                                    Por seguridad deberás cambiar esta contraseña al iniciar sesión.
                                    ''',
                                'no-reply@sistema.com',
                                [usuario.email],
                                fail_silently=False,
                            )
                    else:
                        usuario = Usuario()
                        usuario.email = request.POST.get('email')
                        usuario.username = request.POST.get('email')
                        usuario.first_name = request.POST.get('nombres')
                        usuario.last_name = request.POST.get('apellidos')
                        usuario.persona = persona
                        password_temporal = secrets.token_urlsafe(8)
                        usuario.set_password(password_temporal)
                        usuario.debe_cambiar_password = True
                        # 👉 permisos admin
                        usuario.is_staff = True  # puede entrar al admin
                        usuario.is_active = True  # usuario activo
                        usuario.is_superuser = es_admin
                        usuario.save()
                        usuario.roles.set(roles_ids)

                        send_mail(
                            'Acceso al sistema',
                            f'''
                                Hola {usuario.first_name},

                                Se ha creado una cuenta para ti.

                                Usuario: {usuario.email}
                                Contraseña temporal: {password_temporal}

                                Por seguridad deberás cambiar esta contraseña al iniciar sesión.
                                ''',
                            'no-reply@sistema.com',
                            [usuario.email],
                            fail_silently=False,
                        )
                else:
                    messages.error(request, "Debe seleccionar al menos un rol.")
                    roles = Rol.objects.all().order_by('nombre_rol')
                    dict = {"error": "Debe seleccionar al menos un rol.", "data": request.POST, "tipos": tipos,
                            "roles": roles, "persona": persona, "departamentos": departamentos}
                    return render(request, "pages/empleados_editar.html", dict)

                if request.user.persona:
                    if request.user.persona.id == id:
                        return redirect("modelNewApp:perfil")
                    else:
                        return redirect("modelNewApp:empleados_detalles", persona.id)
                else:
                    return redirect("modelNewApp:empleados_detalles", persona.id)
            else:

                if usuario:
                    persona.empleado.delete()
                if request.user.persona:
                    if request.user.persona.id == id:
                        return redirect("modelNewApp:perfil")
                    else:
                        return redirect("modelNewApp:empleados_detalles", persona.id)
                else:
                    return redirect("modelNewApp:empleados_detalles", persona.id)

    tipos = TipoEmpleado.objects.all().order_by('nombre_tipo')
    roles = Rol.objects.all().order_by('nombre_rol')
    departamentos = Departamento.objects.all().order_by("nombre")
    dict = {"tipos": tipos, "persona": persona, "roles": roles, "roles_persona": roles_persona,
            "departamentos": departamentos}
    return render(request, "pages/empleados_editar.html", dict)


@solo_admin
@login_required
def empleados_activar(request, id):
    persona = get_object_or_404(Persona, id=id)
    persona.activo = True
    persona.save()

    return redirect("modelNewApp:empleados_detalles", persona.id)


@solo_admin
@login_required
def empleados_desactivar(request, id):
    persona = get_object_or_404(Persona, id=id)
    persona.activo = False
    persona.save()

    return redirect("modelNewApp:empleados_detalles", persona.id)


@login_required
def dashboard_control(request):
    return render(request, "pages/dashboard_control.html")


@solo_admin
@login_required
def vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by("placa")
    marcas = Marca.objects.all().order_by("nombre")
    modelos = Modelo.objects.all().order_by("nombre")

    search = request.GET.get('search', '')
    marca = request.GET.get('marca')
    modelo = request.GET.get('modelo')
    orden = request.GET.get('orden')

    if marca:
        vehiculos = vehiculos.filter(marca__id__icontains=marca)

    if modelo:
        vehiculos = vehiculos.filter(modelo__id__icontains=modelo)

    if search:
        vehiculos = vehiculos.filter(
            Q(placa__icontains=search) |
            Q(codigo__icontains=search) |
            Q(marca__nombre__icontains=search) |
            Q(modelo__nombre__icontains=search)
        )

    if orden == "placa":
        vehiculos = vehiculos.order_by("placa")
    elif orden == "-placa":
        vehiculos = vehiculos.order_by("-placa")
    elif orden == "marca":
        vehiculos = vehiculos.order_by("marca")
    elif orden == "-marca":
        vehiculos = vehiculos.order_by("-marca")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/vehiculos_list.html', {
            'vehiculos': vehiculos,
            "orden_actual": orden
        })

    dict = {"vehiculos": vehiculos, "marcas": marcas, "modelos": modelos, "orden_actual": orden}

    return render(request, "pages/vehiculos.html", dict)

@solo_admin
@login_required
def vehiculos_agregar(request):

    if request.POST:

        placa = request.POST.get("placa")
        marca = request.POST.get("marca")
        modelo = request.POST.get("modelo")

        vehiculo = Vehiculo.objects.filter(placa=placa).first()

        if vehiculo:
            print("Ya existe esa placa")
        else:
            vehiculo = Vehiculo()
            vehiculo.placa = placa
            marca, _ = Marca.objects.get_or_create(nombre__iexact=marca, defaults={"nombre": marca})
            vehiculo.marca = marca
            modelo, _ = Modelo.objects.get_or_create(nombre__iexact=modelo, defaults={"nombre": modelo, "marca": marca})
            vehiculo.modelo = modelo
            if request.POST.get("codigo"):
                vehiculo.codigo = request.POST.get("codigo")
            vehiculo.save()

            return redirect("modelNewApp:vehiculos")

    marcas = Marca.objects.all().order_by("nombre")
    modelos = Modelo.objects.all().order_by("nombre")

    dict = {"marcas": marcas, "modelos": modelos}
    return render(request, "pages/vehiculos_agregar.html", dict)

@solo_admin
@login_required
def vehiculos_detalles(request, id):

    vehiculo = Vehiculo.objects.get(id=id)

    historial_accesos = (
        RegistroAcceso.objects
        .filter(vehiculo=vehiculo)
        .select_related('departamento_destino')
        .order_by('-fecha_hora')
    )

    # ──────────────── Paginación ────────────────
    paginator = Paginator(historial_accesos, 20)  # 10 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    dict = {"vehiculo": vehiculo, "page_obj": page_obj}

    return render(request, "pages/vehiculos_detalles.html", dict)

@solo_admin
@login_required
def vehiculos_eliminar(request, id):

    vehiculo = Vehiculo.objects.filter(id=id).first()

    if vehiculo:
        vehiculo.delete()

    return redirect("modelNewApp:vehiculos")

@solo_admin
@login_required
def vehiculos_editar(request, id):

    vehiculo = Vehiculo.objects.filter(id=id).first()
    marcas = Marca.objects.all().order_by("nombre")
    modelos = Modelo.objects.all().order_by("nombre")

    if request.POST:

        placa = request.POST.get("placa")
        marca = request.POST.get("marca")
        modelo = request.POST.get("modelo")

        vehiculo.placa = placa
        marca, _ = Marca.objects.get_or_create(nombre__iexact=marca, defaults={"nombre": marca})
        vehiculo.marca = marca
        modelo, _ = Modelo.objects.get_or_create(nombre__iexact=modelo, defaults={"nombre": modelo, "marca": marca})
        vehiculo.modelo = modelo
        if request.POST.get("codigo"):
            vehiculo.codigo = request.POST.get("codigo")
        else:
            vehiculo.codigo = ""
        vehiculo.save()

        return redirect("modelNewApp:vehiculos_detalles", vehiculo.id)

    dict = {"vehiculo": vehiculo, "marcas": marcas, "modelos": modelos}

    return render(request, "pages/vehiculos_editar.html", dict)

@solo_admin
@login_required
def estadisticos(request):
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    tipo = request.GET.get("tipo")
    tipos = TipoEmpleado.objects.all().order_by('nombre_tipo')

    registros = RegistroAcceso.objects.filter(tipo_movimiento="INGRESO")

    # -------------------------
    # Filtros por fecha
    # -------------------------
    if desde:
        registros = registros.filter(fecha_hora__date__gte=desde)

    if hasta:
        registros = registros.filter(fecha_hora__date__lte=hasta)

    # -------------------------
    # Filtro por tipo de persona
    # -------------------------
    if tipo:
        registros = registros.filter(id_persona__id_tipo__nombre_tipo=tipo)
    # if tipo == "empleado":
    #     registros = registros.filter(id_persona__codigo_p00__isnull=False)
    # elif tipo == "visitante":
    #     registros = registros.filter(id_persona__codigo_p00__isnull=True)

    # -------------------------
    # TOTAL INGRESOS
    # -------------------------
    total_ingresos = registros.count()

    # -------------------------
    # PROMEDIO DIARIO (DÍAS CON ACTIVIDAD)
    # -------------------------
    dias_con_ingresos = (
        registros
        .dates("fecha_hora", "day")
        .count()
    )

    promedio_dias_activos = round(
        total_ingresos / dias_con_ingresos, 2
    ) if dias_con_ingresos > 0 else 0

    # -------------------------
    # PROMEDIO DIARIO (PERÍODO COMPLETO)
    # -------------------------
    if desde and hasta:
        dias_periodo = (
                               date.fromisoformat(hasta) -
                               date.fromisoformat(desde)
                       ).days + 1
        rango_dias = (date.fromisoformat(hasta) - date.fromisoformat(desde)).days + 1
    else:
        primer_registro = registros.order_by("fecha_hora").first()

        if primer_registro:
            fecha_inicio = primer_registro.fecha_hora.date()
            fecha_fin = date.today()
            dias_periodo = (fecha_fin - fecha_inicio).days + 1
            rango_dias = dias_periodo
        else:
            dias_periodo = 0
            rango_dias = 0

    print(total_ingresos)
    print(dias_periodo)
    promedio_periodo = round(
        total_ingresos / dias_periodo, 2
    ) if dias_periodo > 0 else 0
    print(promedio_periodo)

    # -----------------------------
    # DIA CON MAS INGRESOS
    # -----------------------------
    # Agrupar por día
    ingresos_por_dia = list(
        registros
        .annotate(dia=TruncDate('fecha_hora'))
        .values('dia')
        .annotate(cantidad=Count('id'))
        .order_by('dia')
    )

    if ingresos_por_dia:
        dia_mas_ingresos = ingresos_por_dia[0]['dia'].strftime('%d/%m/%Y')
        cantidad_mas_ingresos = ingresos_por_dia[0]['cantidad']
    else:
        dia_mas_ingresos = '-'
        cantidad_mas_ingresos = 0

    # Formatear cantidad_mas_ingresos
    if cantidad_mas_ingresos >= 1000:
        cantidad_mas_ingresos_fmt = f"{cantidad_mas_ingresos / 1000:.1f}k"
        # opcional: quitar decimal si es entero
        if cantidad_mas_ingresos_fmt.endswith(".0k"):
            cantidad_mas_ingresos_fmt = cantidad_mas_ingresos_fmt.replace(".0k", "k")
    else:
        cantidad_mas_ingresos_fmt = str(cantidad_mas_ingresos)

    # Convertir dia a string en formato DD/MM para JS
    for r in ingresos_por_dia:
        r['dia'] = r['dia'].strftime('%d/%m')

    # --------------------------------
    # HORA PICO
    # --------------------------------
    # HORA PICO
    # ingresos_por_hora = (
    #     registros
    #     .annotate(hora=TruncHour('fecha_hora'))
    #     .values('hora')
    #     .annotate(cantidad=Count('id'))
    #     .order_by('-cantidad')
    # )
    #
    # if ingresos_por_hora:
    #     hora_pico = ingresos_por_hora[0]['hora'].strftime('%I:%M %p')
    #
    #     # Formatear cantidad grande
    #     cantidad_hora_pico = ingresos_por_hora[0]['cantidad']
    #     if cantidad_hora_pico >= 1000:
    #         cantidad_hora_pico_fmt = f"{round(cantidad_hora_pico / 1000)}k"
    #     else:
    #         cantidad_hora_pico_fmt = str(cantidad_hora_pico)
    # else:
    #     hora_pico = '-'
    #     cantidad_hora_pico_fmt = '0'

    # ----------------------------------------------------------------------------
    #     Nueva hora pico
    # ----------------------------------------------------------------------------
    datos_hora = (
        registros
        .annotate(hora_num=ExtractHour('fecha_hora'))
        .values('hora_num')
        .annotate(cantidad=Count('id'))
    )

    hora_pico_data = datos_hora.order_by('-cantidad').first()

    if hora_pico_data:
        hora_pico = datetime.strptime(
            str(hora_pico_data['hora_num']), "%H"
        ).strftime('%I:%M %p')

        cantidad = hora_pico_data['cantidad']
        cantidad_hora_pico = (
            f"{round(cantidad / 1000)}k"
            if cantidad >= 1000
            else str(cantidad)
        )
    else:
        hora_pico = "-"
        cantidad_hora_pico = "0"

    fecha_inicio = datetime.strptime(desde, '%Y-%m-%d') if desde else None
    fecha_fin = datetime.strptime(hasta, '%Y-%m-%d') if hasta else None

    # Elegir la granularidad
    if rango_dias <= 30:
        trunc = TruncDay('fecha_hora')
    elif rango_dias <= 90:
        trunc = TruncWeek('fecha_hora', week_start=1)  # semana inicia lunes
    else:
        trunc = TruncMonth('fecha_hora')

    ingresos_por_periodo = (
        registros
        .annotate(periodo=trunc)
        .values('periodo')
        .annotate(cantidad=Count('id'))
        .order_by('periodo')
    )

    for r in ingresos_por_periodo:
        if isinstance(trunc, TruncDay):
            r['periodo'] = r['periodo'].strftime('%d/%m')
        elif isinstance(trunc, TruncWeek):
            # semana: mostrar rango de la semana
            inicio_semana = r['periodo']
            fin_semana = inicio_semana + timedelta(days=6)
            r['periodo'] = f"{inicio_semana.strftime('%d/%m')} - {fin_semana.strftime('%d/%m')}"
        else:  # TruncMonth
            r['periodo'] = r['periodo'].strftime('%b %Y')  # ej: Ene 2026

    # Para gráfico ingresos por hora
    # ingresos_por_hora = list(
    #     registros
    #     .annotate(hora_num=ExtractHour('fecha_hora'))
    #     .values('hora_num')
    #     .annotate(cantidad=Count('id'))
    #     .order_by('hora_num')  # 👈 ahora sí, 0 → 23
    # )
    # for r in ingresos_por_hora:
    #     hora = r['hora_num']
    #     r['hora_label'] = datetime.strptime(str(hora), "%H").strftime("%I %p")

    ingresos_por_hora = list(
        datos_hora.order_by('hora_num')
    )

    for r in ingresos_por_hora:
        r['hora_label'] = datetime.strptime(
            str(r['hora_num']), "%H"
        ).strftime("%I %p")

    # Tipo de persona
    ingresos_por_tipo = (
        registros
        .values(nombre=F('id_persona__id_tipo__nombre_tipo'))
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    # Tabla de accesos
    detalle_accesos = (
        registros
        .values(
            'id_persona',
            'id_persona__nombres',
            'id_persona__apellidos',
            'id_persona__id_tipo__nombre_tipo'
        )
        .annotate(
            total_ingresos=Count('id'),
            ultimo_ingreso=Max('fecha_hora')
        )
        .order_by('-total_ingresos', '-ultimo_ingreso')
    )

    # Para grafico
    ingresos_por_departamento = (
        registros
        .exclude(departamento_destino__isnull=True)
        .values(
            nombre=F('departamento_destino__nombre')
        )
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    # Por persona, por departamento, para gráfico
    ultimos_movimientos = (
        RegistroAcceso.objects
        .values('id_persona')
        .annotate(ultima_fecha=Max('fecha_hora'))
    )
    personas_dentro = RegistroAcceso.objects.filter(
        tipo_movimiento='INGRESO',
        id__in=[
            RegistroAcceso.objects.filter(
                id_persona=m['id_persona'],
                fecha_hora=m['ultima_fecha']
            ).values('id')[:1]
            for m in ultimos_movimientos
        ]
    )
    personas_dentro_por_departamento = (
        personas_dentro
        .exclude(departamento_destino__isnull=True)
        .values(
            nombre=F('departamento_destino__nombre')
        )
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    context = {
        "tipos": tipos,
        "total_ingresos": total_ingresos,
        "promedio_dias_activos": promedio_dias_activos,
        "promedio_periodo": promedio_periodo,
        "dia_mas_ingresos": dia_mas_ingresos,
        "cantidad_mas_ingresos": cantidad_mas_ingresos_fmt,
        "hora_pico": hora_pico,
        "cantidad_hora_pico": cantidad_hora_pico,
        "ingresos_por_dia": ingresos_por_dia,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "ingresos_por_periodo": list(ingresos_por_periodo),
        "ingresos_por_hora": ingresos_por_hora,
        "ingresos_por_tipo": list(ingresos_por_tipo),
        "detalle_accesos": detalle_accesos,
        "ingresos_por_departamento": list(ingresos_por_departamento),
        "personas_dentro_por_departamento": list(personas_dentro_por_departamento),
    }

    return render(request, "pages/estadisticos.html", context)


@solo_admin
@login_required
def reportes(request):
    # -------------------------
    # Datos base para filtros
    # -------------------------
    tipos = TipoEmpleado.objects.all()
    departamentos = Departamento.objects.all()

    # -------------------------
    # Leer filtros
    # -------------------------
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    tipo = request.GET.get("tipo")
    departamento = request.GET.get("departamento")
    tipo_reporte = request.GET.get("reporte", "accesos")

    formato = request.GET.get("formato")

    resultados = None
    columnas = []

    # -------------------------
    # Query base
    # -------------------------
    registros = RegistroAcceso.objects.select_related(
        "id_persona",
        "id_persona__id_tipo",
        "departamento_destino"
    )

    # -------------------------
    # Aplicar filtros
    # -------------------------
    if desde and hasta:
        registros = registros.filter(
            fecha_hora__date__range=[desde, hasta]
        )

    if tipo:
        registros = registros.filter(id_persona__id_tipo__nombre_tipo=tipo)

    if departamento:
        registros = registros.filter(departamento_destino__nombre=departamento)

    if formato == "pdf":
        return exportar_pdf(request, tipo_reporte=tipo_reporte)

    if formato == "excel":
        return exportar_excel(request, tipo_reporte=tipo_reporte)

    if formato == "csv":
        return exportar_csv(request, tipo_reporte=tipo_reporte)

    if tipo_reporte == "accesos":

        columnas = [
            "Fecha",
            "Persona",
            "Tipo",
            "Movimiento",
            "Departamento"
        ]

        resultados = [
            {
                "fecha": r.fecha_hora.strftime("%d/%m/%Y %I:%M %p"),
                "persona": f"{r.id_persona.nombres} {r.id_persona.apellidos}",
                "tipo": r.id_persona.id_tipo.nombre_tipo,
                "movimiento": r.get_tipo_movimiento_display(),
                "departamento": r.departamento_destino.nombre if r.departamento_destino else None
            }
            for r in registros.order_by("-fecha_hora")
        ]



    elif tipo_reporte == "personas":

        columnas = [
            "Persona",
            "Tipo",
            "Total ingresos",
            "Último ingreso"
        ]

        resultados = [
            {
                "persona": f"{r['id_persona__nombres']} {r['id_persona__apellidos']}",
                "tipo": r['id_persona__id_tipo__nombre_tipo'],
                "total": r['total_ingresos'],
                "ultimo": r['ultimo_ingreso'].strftime("%d/%m/%Y %I:%M %p") if r['ultimo_ingreso'] else None
            }

            for r in (
                registros
                .filter(tipo_movimiento="INGRESO")
                .values(
                    "id_persona__nombres",
                    "id_persona__apellidos",
                    "id_persona__id_tipo__nombre_tipo"
                )

                .annotate(
                    total_ingresos=Count("id"),
                    ultimo_ingreso=Max("fecha_hora")
                )
            )
        ]


    elif tipo_reporte == "diario":

        columnas = [
            "Fecha",
            "Ingresos",
            "Salidas"
        ]

        resultados = (
            registros
            .values("fecha_hora__date")
            .annotate(
                ingresos=Count("id", filter=models.Q(tipo_movimiento="INGRESO")),
                salidas=Count("id", filter=models.Q(tipo_movimiento="EGRESO")),
            )
            .order_by("-fecha_hora__date")
        )

    elif tipo_reporte == "tipo":

        columnas = [
            "Tipo de persona",
            "Total ingresos"
        ]

        resultados = (
            registros
            .filter(tipo_movimiento="INGRESO")
            .values("id_persona__id_tipo__nombre_tipo")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

    elif tipo_reporte == "departamento":

        columnas = [
            "Departamento",
            "Total ingresos"
        ]

        resultados = (
            registros
            .filter(
                tipo_movimiento="INGRESO",
                departamento_destino__isnull=False
            )
            .values("departamento_destino__nombre")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

    paginator = Paginator(resultados, 20)  # 10 filas por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "tipos": tipos,
        "departamentos": departamentos,
        "resultados": resultados,
        "columnas": columnas,
        "filtros": request.GET,

        "page_obj": page_obj,
        "request": request,
    }

    return render(request, "pages/reportes.html", context)


@solo_admin
@login_required
def perfil(request):
    persona = request.user.persona

    dict = {"persona": persona}

    return render(request, "pages/perfil.html", dict)


def exportar_historial_pdf(request, persona_id):
    persona = Persona.objects.get(id=persona_id)
    registros = RegistroAcceso.objects.filter(id_persona=persona).order_by('fecha_hora')

    # Crear respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historial_{persona.nombres}.pdf"'

    # Crear PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Historial de accesos: {persona.nombres} {persona.apellidos}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Fecha y hora")
    c.drawString(200, y, "Tipo movimiento")
    c.drawString(350, y, "Departamento")
    y -= 20

    c.setFont("Helvetica", 12)
    for reg in registros:
        if y < 50:  # nueva página
            c.showPage()
            y = height - 50

        # c.drawString(50, y, reg.fecha_hora.strftime("%d/%m/%Y %I:%M %p"))
        fecha_local = timezone.localtime(reg.fecha_hora)

        c.drawString(
            50,
            y,
            fecha_local.strftime("%d/%m/%Y %I:%M %p")
        )

        c.drawString(200, y, reg.tipo_movimiento)
        depto = reg.departamento_destino.nombre if reg.departamento_destino else "-"
        c.drawString(350, y, depto)
        y -= 20

    c.save()
    return response

def exportar_historial_pdf_vehiculos(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(id=vehiculo_id)
    registros = RegistroAcceso.objects.filter(vehiculo=vehiculo).order_by('fecha_hora')

    # Crear respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="historial_{vehiculo.placa}.pdf"'

    # Crear PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Historial de accesos: Vehículo con placa {vehiculo.placa}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Fecha y hora")
    c.drawString(200, y, "Tipo movimiento")
    c.drawString(350, y, "Departamento")
    y -= 20

    c.setFont("Helvetica", 12)
    for reg in registros:
        if y < 50:  # nueva página
            c.showPage()
            y = height - 50

        # c.drawString(50, y, reg.fecha_hora.strftime("%d/%m/%Y %I:%M %p"))
        fecha_local = timezone.localtime(reg.fecha_hora)

        c.drawString(
            50,
            y,
            fecha_local.strftime("%d/%m/%Y %I:%M %p")
        )

        c.drawString(200, y, reg.tipo_movimiento)
        depto = reg.departamento_destino.nombre if reg.departamento_destino else "-"
        c.drawString(350, y, depto)
        y -= 20

    c.save()
    return response


def exportar_historial_excel(request, persona_id):
    persona = Persona.objects.get(id=persona_id)
    registros = RegistroAcceso.objects.filter(id_persona=persona).order_by('fecha_hora')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial"

    # Encabezados
    headers = ["Fecha y hora", "Tipo movimiento", "Departamento"]
    for col_num, header in enumerate(headers, 1):
        ws[f"{get_column_letter(col_num)}1"] = header

    # Datos
    for row_num, reg in enumerate(registros, 2):
        ws[f"A{row_num}"] = reg.fecha_hora.strftime("%d/%m/%Y %I:%M %p")
        ws[f"B{row_num}"] = reg.tipo_movimiento
        ws[f"C{row_num}"] = reg.departamento_destino.nombre if reg.departamento_destino else "-"

    # Respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename=historial_{persona.nombres}.xlsx'
    wb.save(response)
    return response

def exportar_historial_excel_vehiculos(request, vehiculo_id):
    vehiculo = Vehiculo.objects.get(id=vehiculo_id)
    registros = RegistroAcceso.objects.filter(vehiculo=vehiculo).order_by('fecha_hora')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial"

    # Encabezados
    headers = ["Fecha y hora", "Tipo movimiento", "Departamento"]
    for col_num, header in enumerate(headers, 1):
        ws[f"{get_column_letter(col_num)}1"] = header

    # Datos
    for row_num, reg in enumerate(registros, 2):
        fecha_local = timezone.localtime(reg.fecha_hora)
        # ws[f"A{row_num}"] = reg.fecha_hora.strftime("%d/%m/%Y %I:%M %p")
        ws[f"A{row_num}"] = fecha_local.strftime("%d/%m/%Y %I:%M %p")
        ws[f"B{row_num}"] = reg.tipo_movimiento
        ws[f"C{row_num}"] = reg.departamento_destino.nombre if reg.departamento_destino else "-"

    # Respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename=historial_{vehiculo.placa}.xlsx'
    wb.save(response)
    return response


def obtener_queryset_reporte(request):
    qs = RegistroAcceso.objects.select_related(
        "id_persona",
        "departamento_destino",
    )

    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")
    tipo = request.GET.get("tipo")
    departamento = request.GET.get("departamento")

    if desde:
        qs = qs.filter(fecha_hora__date__gte=desde)

    if hasta:
        qs = qs.filter(fecha_hora__date__lte=hasta)

    if tipo:
        qs = qs.filter(id_persona__id_tipo__nombre_tipo=tipo)

    if departamento:
        qs = qs.filter(departamento_destino__id=departamento)

    return qs.order_by("-fecha_hora")


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def exportar_pdf(request, tipo_reporte="accesos"):
    queryset = obtener_queryset_reporte(request)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=reporte_accesos.pdf"

    doc = SimpleDocTemplate(response, pagesize=A4)
    elementos = []

    # Tabla: encabezados
    # ---------------------------
    # Encabezados y filas
    # ---------------------------
    if tipo_reporte == "accesos":
        columnas = ["Fecha y hora", "Persona", "Tipo", "Movimiento", "Departamento"]
        data = [columnas]
        for r in queryset:
            data.append([
                r.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                f"{r.id_persona.nombres} {r.id_persona.apellidos}",
                r.id_persona.id_tipo.nombre_tipo,
                r.get_tipo_movimiento_display(),
                r.departamento_destino.nombre if r.departamento_destino else "-"
            ])



    elif tipo_reporte == "personas":

        columnas = ["Persona", "Tipo", "Total ingresos", "Último ingreso"]
        data = [columnas]

        # Crear queryset filtrado igual que obtener_queryset_reporte
        qs = RegistroAcceso.objects.filter(tipo_movimiento="INGRESO")
        desde = request.GET.get("desde")
        hasta = request.GET.get("hasta")
        tipo = request.GET.get("tipo")
        departamento = request.GET.get("departamento")

        if desde:
            qs = qs.filter(fecha_hora__date__gte=desde)

        if hasta:
            qs = qs.filter(fecha_hora__date__lte=hasta)

        if tipo:
            qs = qs.filter(id_persona__id_tipo__nombre_tipo=tipo)

        if departamento:
            qs = qs.filter(departamento_destino__nombre=departamento)

        # Ahora sí agregamos por persona
        qs = qs.values(
            "id_persona__nombres",
            "id_persona__apellidos",
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(
            total_ingresos=Count("id"),
            ultimo_ingreso=Max("fecha_hora")
        ).order_by("id_persona__apellidos")

        for r in qs:
            data.append([
                f"{r['id_persona__nombres']} {r['id_persona__apellidos']}",
                r['id_persona__id_tipo__nombre_tipo'],
                r['total_ingresos'],
                r['ultimo_ingreso'].strftime("%d/%m/%Y %H:%M") if r['ultimo_ingreso'] else "-"
            ])

    elif tipo_reporte == "diario":
        columnas = ["Fecha", "Ingresos", "Salidas"]
        data = [columnas]

        qs = queryset.values("fecha_hora__date").annotate(
            ingresos=Count("id", filter=models.Q(tipo_movimiento="INGRESO")),
            salidas=Count("id", filter=models.Q(tipo_movimiento="EGRESO"))
        ).order_by("fecha_hora__date")

        for r in qs:
            data.append([
                r['fecha_hora__date'].strftime("%d/%m/%Y"),
                r['ingresos'],
                r['salidas']
            ])

    elif tipo_reporte == "tipo":
        columnas = ["Tipo de persona", "Total ingresos"]
        data = [columnas]

        qs = queryset.filter(tipo_movimiento="INGRESO").values(
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(total=Count("id")).order_by("-total")

        for r in qs:
            data.append([
                r['id_persona__id_tipo__nombre_tipo'],
                r['total']
            ])

    elif tipo_reporte == "departamento":
        columnas = ["Departamento", "Total ingresos"]
        data = [columnas]

        qs = queryset.filter(
            tipo_movimiento="INGRESO",
            departamento_destino__isnull=False
        ).values(
            "departamento_destino__nombre"
        ).annotate(total=Count("id")).order_by("-total")

        for r in qs:
            data.append([
                r['departamento_destino__nombre'],
                r['total']
            ])

    colWidths = []
    for col_idx in range(len(data[0])):
        max_width = max(stringWidth(str(row[col_idx]), "Helvetica", 10) for row in data)
        colWidths.append(max_width + 10)

    tabla = Table(data, colWidths=colWidths)

    # tabla = Table(data, colWidths=[100, 150, 80, 150])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    return response


def exportar_excel(request, tipo_reporte="accesos"):
    queryset = obtener_queryset_reporte(request)

    # Crear workbook y hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte"

    filas = []
    columnas = []

    # ------------------------
    # Generar encabezados
    # ------------------------
    if tipo_reporte == "accesos":
        columnas = ["Fecha y hora", "Persona", "Tipo", "Movimiento", "Departamento"]
        filas = [
            [
                r.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                f"{r.id_persona.nombres} {r.id_persona.apellidos}",
                r.id_persona.id_tipo.nombre_tipo,
                r.get_tipo_movimiento_display(),
                r.departamento_destino.nombre if r.departamento_destino else "-"
            ]
            for r in queryset
        ]

    elif tipo_reporte == "personas":

        columnas = ["Persona", "Tipo", "Total ingresos", "Último ingreso"]
        # Crear filas usando values + annotate igual que la vista previa
        qs = queryset.filter(tipo_movimiento="INGRESO").values(
            "id_persona__nombres",
            "id_persona__apellidos",
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(
            total_ingresos=Count("id"),
            ultimo_ingreso=Max("fecha_hora")
        ).order_by("id_persona__nombres")

        filas = [
            [
                f"{r['id_persona__nombres']} {r['id_persona__apellidos']}",
                r['id_persona__id_tipo__nombre_tipo'],
                r['total_ingresos'],
                r['ultimo_ingreso'].strftime("%d/%m/%Y %H:%M") if r['ultimo_ingreso'] else "-"
            ]

            for r in qs
        ]

    elif tipo_reporte == "diario":
        columnas = ["Fecha", "Ingresos", "Salidas"]
        qs = queryset.values("fecha_hora__date").annotate(
            ingresos=Count("id", filter=models.Q(tipo_movimiento="INGRESO")),
            salidas=Count("id", filter=models.Q(tipo_movimiento="EGRESO"))
        ).order_by("fecha_hora__date")
        filas = [
            [
                r['fecha_hora__date'].strftime("%d/%m/%Y"),
                r['ingresos'],
                r['salidas']
            ]
            for r in qs
        ]

    elif tipo_reporte == "tipo":
        columnas = ["Tipo de persona", "Total ingresos"]
        qs = queryset.filter(tipo_movimiento="INGRESO").values(
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(total=Count("id")).order_by("-total")
        filas = [
            [r['id_persona__id_tipo__nombre_tipo'], r['total']]
            for r in qs
        ]

    elif tipo_reporte == "departamento":
        columnas = ["Departamento", "Total ingresos"]
        qs = queryset.filter(tipo_movimiento="INGRESO", departamento_destino__isnull=False).values(
            "departamento_destino__nombre"
        ).annotate(total=Count("id")).order_by("-total")
        filas = [
            [r['departamento_destino__nombre'], r['total']]
            for r in qs
        ]

    # ------------------------
    # Escribir encabezados
    # ------------------------
    for col_num, column_title in enumerate(columnas, 1):
        cell = ws.cell(row=1, column=col_num, value=column_title)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # ------------------------
    # Escribir filas
    # ------------------------
    for row_num, row_data in enumerate(filas, 2):
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(horizontal="left")

    # ------------------------
    # Ajustar ancho columnas
    # ------------------------
    for i, col in enumerate(columnas, 1):
        max_length = max(
            [len(str(row[i - 1])) for row in filas] + [len(col)]
        )
        ws.column_dimensions[get_column_letter(i)].width = max_length + 2

    # ------------------------
    # Devolver archivo
    # ------------------------
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=reporte.xlsx"
    wb.save(response)
    return response


def exportar_csv(request, tipo_reporte="accesos"):
    queryset = obtener_queryset_reporte(request)

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="reporte.csv"'

    response.write("\ufeff")  # BOM para Excel

    writer = csv.writer(response)

    columnas = []
    filas = []

    # ------------------------
    # ACCESOS DETALLADOS
    # ------------------------
    if tipo_reporte == "accesos":
        columnas = ["Fecha y hora", "Persona", "Tipo", "Movimiento", "Departamento"]

        filas = [
            [
                r.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                f"{r.id_persona.nombres} {r.id_persona.apellidos}",
                r.id_persona.id_tipo.nombre_tipo,
                r.get_tipo_movimiento_display(),
                r.departamento_destino.nombre if r.departamento_destino else "-"
            ]
            for r in queryset
        ]

    # ------------------------
    # RESUMEN POR PERSONA
    # ------------------------
    elif tipo_reporte == "personas":
        columnas = ["Persona", "Tipo", "Total ingresos", "Último ingreso"]

        qs = queryset.filter(tipo_movimiento="INGRESO").values(
            "id_persona__nombres",
            "id_persona__apellidos",
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(
            total_ingresos=Count("id"),
            ultimo_ingreso=Max("fecha_hora")
        ).order_by("id_persona__apellidos")

        filas = [
            [
                f"{r['id_persona__nombres']} {r['id_persona__apellidos']}",
                r['id_persona__id_tipo__nombre_tipo'],
                r['total_ingresos'],
                r['ultimo_ingreso'].strftime("%d/%m/%Y %H:%M") if r['ultimo_ingreso'] else "-"
            ]
            for r in qs
        ]

    # ------------------------
    # RESUMEN DIARIO
    # ------------------------
    elif tipo_reporte == "diario":
        columnas = ["Fecha", "Ingresos", "Salidas"]

        qs = queryset.values("fecha_hora__date").annotate(
            ingresos=Count("id", filter=models.Q(tipo_movimiento="INGRESO")),
            salidas=Count("id", filter=models.Q(tipo_movimiento="EGRESO"))
        ).order_by("fecha_hora__date")

        filas = [
            [
                r["fecha_hora__date"].strftime("%d/%m/%Y"),
                r["ingresos"],
                r["salidas"]
            ]
            for r in qs
        ]

    # ------------------------
    # POR TIPO DE PERSONA
    # ------------------------
    elif tipo_reporte == "tipo":
        columnas = ["Tipo de persona", "Total ingresos"]

        qs = queryset.filter(tipo_movimiento="INGRESO").values(
            "id_persona__id_tipo__nombre_tipo"
        ).annotate(total=Count("id")).order_by("-total")

        filas = [
            [r["id_persona__id_tipo__nombre_tipo"], r["total"]]
            for r in qs
        ]

    # ------------------------
    # POR DEPARTAMENTO
    # ------------------------
    elif tipo_reporte == "departamento":
        columnas = ["Departamento", "Total ingresos"]

        qs = queryset.filter(
            tipo_movimiento="INGRESO",
            departamento_destino__isnull=False
        ).values(
            "departamento_destino__nombre"
        ).annotate(total=Count("id")).order_by("-total")

        filas = [
            [r["departamento_destino__nombre"], r["total"]]
            for r in qs
        ]

    # ------------------------
    # Escribir CSV
    # ------------------------
    writer.writerow(columnas)
    writer.writerows(filas)

    return response


def recuperar_contraseña(request):
    dict = {}

    if request.POST:

        usuario = Usuario.objects.filter(email=request.POST["email"]).first()

        if usuario:

            password_temporal = secrets.token_urlsafe(8)
            usuario.set_password(password_temporal)
            usuario.debe_cambiar_password = True
            usuario.save()
            send_mail(
                'Acceso al sistema',
                f'''
                            Hola {usuario.first_name},
    
                            Se ha cambiar su dirección de correo electrónico.
    
                            Usuario: {usuario.email}
                            Contraseña temporal: {password_temporal}
    
                            Por seguridad deberás cambiar esta contraseña al iniciar sesión.
                            ''',
                'no-reply@sistema.com',
                [request.POST['email']],
                fail_silently=False,
            )
            return redirect('modelNewApp:home')
        else:
            messages.error(request, "No existe un usuario con ese correo.")
            return render(
                request,
                "pages/recuperar_contraseña.html",
                {
                    "error": "No existe un usuario con ese correo.",
                })

    return render(request, "pages/recuperar_contraseña.html", dict)

# ---------------------------------------------------------------------------------------
#     Respaldo simple de la base de datos
# ---------------------------------------------------------------------------------------

import os
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.conf import settings

DB_FILE = os.path.join(settings.BASE_DIR, 'db.sqlite3')


def db_panel(request):
    return render(request, 'pages/admin_db_panel.html')


def db_download(request):
    if os.path.exists(DB_FILE):
        return FileResponse(
            open(DB_FILE, 'rb'),
            as_attachment=True,
            filename="db_backup.sqlite3"
        )
    return HttpResponse("Base de datos no encontrada", status=404)


def db_restore(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('db_file')

        if uploaded_file and uploaded_file.name.endswith('.sqlite3'):
            # 🔴 MUY IMPORTANTE:
            # Cerrar conexiones antes de sobrescribir
            from django.db import connection
            connection.close()

            with open(DB_FILE, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            return redirect('modelNewApp:db_panel')

    return HttpResponse("Método no permitido", status=405)
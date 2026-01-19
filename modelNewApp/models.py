from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser

# ------------------------------------------------------
# Tipo de persona (empleado, visitante, etc.)
# ------------------------------------------------------
class TipoEmpleado(models.Model):
    nombre_tipo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_tipo


# ------------------------------------------------------
# Departamento
# ------------------------------------------------------
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# ------------------------------------------------------
# Personas (empleados y visitantes)
# ------------------------------------------------------
class Persona(models.Model):
    TIPO_SEXO = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )

    id_tipo = models.ForeignKey(TipoEmpleado, on_delete=models.PROTECT, related_name='personas')
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personas'
    )
    codigo_p00 = models.CharField(max_length=20, unique=True, null=True, blank=True)  # solo empleados
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100, blank=True, null=True)  # opcional para visitantes
    cedula = models.CharField(max_length=20, unique=True)
    sexo = models.CharField(max_length=1, choices=TIPO_SEXO, blank=True, null=True)
    activo = models.BooleanField(default=True)  # solo empleados
    fecha_registro = models.DateTimeField(auto_now_add=True)

    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.nombres} {self.apellidos or ''}".strip()

# ------------------------------------------------------
# Estados de los registros (ingreso, egreso, completo, etc.)
# ------------------------------------------------------
class Estado(models.Model):
    nombre_estado = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_estado



# ------------------------------------------------------
# Registro de acceso
# ------------------------------------------------------
class RegistroAcceso(models.Model):
    TIPO_MOVIMIENTO = (
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    )

    departamento_destino = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros'
    )

    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='registros')
    fecha_hora = models.DateTimeField(blank=True, null=True)
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)

    def __str__(self):
        return f"{self.id_persona} - {self.tipo_movimiento} - {self.fecha_hora}"

# ------------------------------------------------------
# Usuarios del sistema (solo empleados que acceden al dashboard)
# ------------------------------------------------------
class Usuario(AbstractUser):
    persona = models.OneToOneField(Persona, on_delete=models.SET_NULL, related_name='empleado', null=True, blank=True)
    email = models.EmailField(unique=True)
    #password = models.CharField(max_length=128)  # Django maneja hashing
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    debe_cambiar_password = models.BooleanField(default=True)

    def __str__(self):
        return self.email

# ------------------------------------------------------
# Roles del sistema
# ------------------------------------------------------
class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    usuarios = models.ManyToManyField(Usuario, through='UsuarioRol', related_name='roles')

    def __str__(self):
        return self.nombre_rol

# ------------------------------------------------------
# Tabla intermedia Usuario-Rol
# ------------------------------------------------------
class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')

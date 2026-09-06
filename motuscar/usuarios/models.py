from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.

class User(AbstractUser):
    
    #Tipos de usuarios que manejamos
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('mecanico', 'Mecánico'),
        ('proveedor', 'Proveedor'),
        ('admin','Administrador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='cliente'
    )
    
    #Campos o Atributos Comunes
    
    telefono = models.CharField(max_length=11, blank=True)
    direccion = models.TextField(blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    #Meta-info
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"
    
#Perfil Cliente Comun
class Cliente(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_cliente'
    )

 
#Perfil Mecánico    
class Mecanico(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_mecanico'
    )
    
    #Campos específicos del Mecánico
    
    especialidades = models.CharField(max_length=200, blank=True)
    experiencia = models.CharField(max_length=200, blank=False)
    tiene_taller = models.BooleanField(default=False)
    direccion_taller = models.TextField(blank=False)
    horario_atencion = models.CharField(max_length=100, blank=False)
    
    #Rating y Reputación
    rating_promedio = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    servicios_completados = models.PositiveIntegerField(default=0)
    
    #Documentacion
    rut = models.CharField(max_length=12, unique=True, blank=False)
    licencia_conducir = models.CharField(max_length=20, blank=True)
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Mecánico"
        verbose_name_plural = "Mecánicos"
        
    def __str__(self):
        return f"Mecánico: {self.user.get_full_name()}"
    
#Perfil Proveedor
class Proveedor(models.Model):
    TIPO_PROVEEDOR_CHOICES = [
        ('empresa','Empresa'),
        ('individual', 'Persona Natural/Minorista'),
        ('taller', 'Taller Mecánico'),
        ('importador', 'Importador Directo'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_proveedor'
    )
    
    tipo_proveedor = models.CharField(
        max_length=15,
        choices=TIPO_PROVEEDOR_CHOICES,
        default='individual'
    )

    nombre_comercial = models.CharField(max_length=200)
    
    rut_empresa = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        verbose_name='RUT Empresa',
    )
    
    rut_personal = models.CharField(max_length=12,blank=True,null=True,verbose_name='RUT Personal')
    giro = models.CharField(max_length=200, blank=True)
    
    def clean(self):
        """Validación¿"""
        super().clean()
        
        if not self.rut_empresa and not self.rut_personal:
            raise ValidationError('Debe proporcionar al menos un rut (empresa o personal)')
        
        if self.tipo_proveedor == 'empresa' and not self.rut_empresa:
            raise ValidationError('Las empresas deben tener RUT de empresa')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
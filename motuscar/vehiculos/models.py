from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

# Create your models here.

class Vehiculos(models.Model):
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehiculo'
    )
    
    TIPO_CHOICES = [
        ('auto','Automóvil'),
        ('camioneta','Camioneta'),
        ('moto','Motocicleta'),
        ('bus','Bus'),
        ('camion','Camión'),
    ]
    
    TIPO_COMBUSTIBLE_CHOICES = [
        ('gasolina','Gasolina'),
        ('diesel','Diésel'),
        ('electrico','Eléctrico'),
        ('hibrido','Híbrido'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('en_taller','En Taller'),
        ('inactivo', 'Inactivo'),
    ]
    
    #Características
    patente = models.CharField(max_length=8, unique=True, verbose_name='Patente')
    marca = models.CharField(max_length=50, blank=False)
    modelo = models.CharField(max_length=50, blank=False)
    año = models.PositiveIntegerField(default=0000)
    nro_chasis = models.CharField(max_length=50, blank=True, null=True)
    tipo_combustible = models.CharField(max_length=20, choices=TIPO_COMBUSTIBLE_CHOICES)
    tipo_vehiculo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    #estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    #Fechas
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_servicio = models.DateField(null=True, blank=True)
    
    #Observaciones
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['-fecha_ingreso']
        
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"
    
    def info_completa(self):
        return f"{self.año} {self.marca} {self.modelo} - {self.patente}"
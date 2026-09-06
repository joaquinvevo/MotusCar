# motuscar/ventas/models.py
from django.conf import settings
from django.db import models
from inventario.models import Producto


class Order(models.Model):
    """
    Pedido guest-friendly:
    - user es opcional (guest = NULL)
    - email_contacto obligatorio para identificar/comunicar
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    email_contacto = models.EmailField()
    nombre_contacto = models.CharField(max_length=120, blank=True)

    direccion_envio = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True)
    comuna = models.CharField(max_length=100, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    pagado = models.BooleanField(default=False)
    total_clp = models.PositiveIntegerField(default=0)  # snapshot del total en CLP

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        who = self.user.get_username() if self.user_id else self.email_contacto
        return f"Order #{self.pk} - {who}"
    

class Valoracion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="valoraciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    orden = models.ForeignKey(Order, on_delete=models.CASCADE) # Vincula con la compra real
    puntuacion = models.PositiveSmallIntegerField(default=5)
    comentario = models.TextField(max_length=500, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valoración de {self.usuario} para {self.producto}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=64)
    nombre = models.CharField(max_length=200)
    precio_unitario = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(default=1)

    # Datos opcionales de logística/oferta
    proveedor = models.CharField(max_length=200, blank=True)
    region = models.CharField(max_length=100, blank=True)
    comuna = models.CharField(max_length=100, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return f"{self.nombre} x{self.cantidad}"

    @property
    def subtotal(self) -> int:
        return int(self.precio_unitario) * int(self.cantidad)

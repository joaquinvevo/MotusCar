from django.db import models

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length= 300, blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=100)
    codigo_sku = models.CharField(max_length=50, verbose_name='Código SKU', unique=True)
    
    #Faltan los models de los usuarios todavía :(
    #Ya no :D
    
    proveedor = models.ForeignKey(
        'usuarios.Proveedor',
        on_delete=models.CASCADE,
        related_name='productos'
    )
    
    #Ahora las Categorías son definidas de forma manual en vez de un pre-set
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    
    precio_unitario = models.PositiveIntegerField(default=0) #No cambiar el tipo de atributo porque este es para peso chileno CLP
    descripcion = models.TextField(max_length=500, blank=True, help_text="Descripción del Producto")
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    stock_actual = models.PositiveIntegerField(default=0) #Trackeo
    stock_minimo = models.PositiveIntegerField(default=5) #Trackeo
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_ingreso'] #Ordena por el más reciente
        
    def __str__(self):
        return f"{self.nombre_producto}({self.codigo_sku})"
    
    def reabastecer(self):
        return self.stock_actual <= self.stock_minimo
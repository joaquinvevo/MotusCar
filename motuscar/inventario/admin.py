from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "activa")
    search_fields = ("nombre",)
    list_filter = ("activa",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id_producto", "nombre_producto", "codigo_sku",
                    "precio_unitario", "stock_actual", "categoria", "proveedor")
    list_filter  = ("categoria", "proveedor")
    search_fields = ("nombre_producto", "codigo_sku")
    autocomplete_fields = ("categoria", "proveedor")  # ahora sí, Proveedor tiene admin

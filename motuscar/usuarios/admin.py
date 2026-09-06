from django.contrib import admin
from .models import Proveedor, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "tipo_usuario", "is_active", "date_joined")
    search_fields = ("username", "email")

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tipo_proveedor", "nombre_comercial",
                    "rut_empresa", "rut_personal", "giro")
    search_fields = ("nombre_comercial", "rut_empresa", "rut_personal", "user__username", "user__email")

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("sku","nombre","precio_unitario","cantidad","subtotal")
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","email_contacto","user","pagado","total_clp","creado")
    list_filter = ("pagado","region","comuna","creado")
    search_fields = ("email_contacto","user__username","user__email")
    date_hierarchy = "creado"
    inlines = [OrderItemInline]

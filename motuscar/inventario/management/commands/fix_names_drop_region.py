from django.core.management.base import BaseCommand
from inventario.models import Producto

class Command(BaseCommand):
    help = "Elimina el sufijo ' · Región' del nombre de productos seed."

    def handle(self, *args, **opts):
        n = 0
        for p in Producto.objects.all().only("id_producto", "nombre_producto"):
            if " · " in p.nombre_producto:
                p.nombre_producto = p.nombre_producto.split(" · ", 1)[0].strip()
                p.save(update_fields=["nombre_producto"])
                n += 1
        self.stdout.write(self.style.SUCCESS(f"Nombres normalizados: {n}"))

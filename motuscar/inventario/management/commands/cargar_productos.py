from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Proveedor
from inventario.models import Categoria, Producto

class Command(BaseCommand):
    help = "Carga categorías y productos demo"

    def handle(self, *args, **opts):
        User = get_user_model()
        u, _ = User.objects.get_or_create(
            username="prov_demo",
            defaults={"email":"prov@demo.cl","tipo_usuario":"proveedor","is_active":True}
        )
        if not u.has_usable_password():
            u.set_password("12345678"); u.save()

        prov, _ = Proveedor.objects.get_or_create(
            user=u,
            defaults={"tipo_proveedor":"empresa","nombre_comercial":"ACME Repuestos",
                      "rut_empresa":"76.123.456-7","giro":"Venta de repuestos"}
        )

        cats = {
            "Filtros": "Filtros de motor/aire/combustible",
            "Frenos": "Pastillas, discos y kits",
            "Baterías": "Baterías 35Ah–75Ah",
            "Aceites": "Aceites 5W30, 10W40",
            "Iluminación": "H4, H7, LED",
            "Neumáticos": "Medidas comunes",
        }
        cat_objs = {n: Categoria.objects.get_or_create(
            nombre=n, defaults={"descripcion": d, "activa": True})[0]
            for n, d in cats.items()
        }

        items = [
            ("Filtro de aceite 1.6","FILT-OIL-1600","Filtros",5990,20),
            ("Filtro de aire estándar","FILT-AIR-STD","Filtros",8990,15),
            ("Filtro de combustible","FILT-FUEL-01","Filtros",7990,18),
            ("Pastillas freno delantera C","FRE-PAD-C01","Frenos",22990,12),
            ("Disco freno ventilado 256mm","FRE-DISC-256","Frenos",45990,8),
            ("Batería 45Ah libre mantención","BAT-45AH","Baterías",69990,7),
            ("Batería 65Ah libre mantención","BAT-65AH","Baterías",89990,5),
            ("Aceite 5W30 sintético 4L","OIL-5W30-4L","Aceites",25990,14),
            ("Aceite 10W40 semisintético 4L","OIL-10W40-4L","Aceites",19990,10),
            ("Ampolleta H4 60/55W","LUM-H4-6055","Iluminación",4990,30),
            ("Kit LED H7 6000K","LUM-H7-LED","Iluminación",24990,9),
            ("Neumático 195/65 R15","NEU-1956515","Neumáticos",74990,6),
            ("Neumático 205/55 R16","NEU-2055516","Neumáticos",89990,4),
        ]

        creados = 0
        for nombre, sku, cat_name, precio, stock in items:
            c = cat_objs[cat_name]
            _, made = Producto.objects.get_or_create(
                codigo_sku=sku,
                defaults={
                    "nombre_producto": nombre,
                    "precio_unitario": precio,
                    "descripcion": "",
                    "stock_actual": stock,
                    "stock_minimo": 5,
                    "categoria": c,
                    "proveedor": prov,
                }
            )
            if made: creados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed OK -> Categorías: {len(cat_objs)} | Productos nuevos: {creados}"
        ))

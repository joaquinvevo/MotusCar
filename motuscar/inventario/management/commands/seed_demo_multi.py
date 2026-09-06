from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from usuarios.models import Proveedor
from inventario.models import Categoria, Producto

import random
import re

# Usar el catálogo si existe
try:
    from ventas.geo_cl import COMUNAS_POR_REGION as CATALOGO
except Exception:
    CATALOGO = {
        "Metropolitana de Santiago": ["Santiago", "Providencia", "Las Condes", "Maipú", "Puente Alto", "La Florida", "Ñuñoa", "Recoleta"],
        "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana", "San Antonio", "Quillota"],
        "Biobío": ["Concepción", "Talcahuano", "San Pedro de la Paz", "Los Ángeles", "Coronel"],
        "Los Lagos": ["Puerto Montt", "Puerto Varas", "Osorno", "Castro", "Ancud"],
        "La Araucanía": ["Temuco", "Padre Las Casas", "Villarrica", "Pucón"],
    }

BASE_ITEMS = [
    ("Filtro de aceite 1.6", "FILT-OIL-1600", "Filtros", 5990, 20),
    ("Filtro de aire estándar", "FILT-AIR-STD", "Filtros", 8990, 15),
    ("Filtro de combustible", "FILT-FUEL-01", "Filtros", 7990, 18),
    ("Pastillas freno delantera C", "FRE-PAD-C01", "Frenos", 22990, 12),
    ("Disco freno ventilado 256mm", "FRE-DISC-256", "Frenos", 45990, 8),
    ("Batería 45Ah libre mantención", "BAT-45AH", "Baterías", 69990, 7),
    ("Aceite 5W30 sintético 4L", "OIL-5W30-4L", "Aceites", 25990, 14),
    ("Ampolleta H4 60/55W", "LUM-H4-6055", "Iluminación", 4990, 30),
    ("Neumático 205/55 R16", "NEU-2055516", "Neumáticos", 89990, 4),
]

CATS = {
    "Filtros": "Filtros de motor/aire/combustible",
    "Frenos": "Pastillas, discos y kits",
    "Baterías": "Baterías 35Ah–75Ah",
    "Aceites": "Aceites 5W30, 10W40",
    "Iluminación": "H4, H7, LED",
    "Neumáticos": "Medidas comunes",
}

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

class Command(BaseCommand):
    help = "Crea múltiples proveedores en varias regiones y carga productos para cada uno."

    def add_arguments(self, parser):
        parser.add_argument("--providers", type=int, default=5,
                            help="Cantidad de proveedores a crear (default: 5).")
        parser.add_argument("--per-provider", type=int, default=6,
                            help="Productos por proveedor (default: 6).")
        parser.add_argument("--regions", type=str,
                            help="Lista separada por comas de regiones a usar (usa nombres exactos). Si se omite, recorre el catálogo.")
        parser.add_argument("--reset", action="store_true",
                            help="Si existe el usuario, reasigna región/comuna y crea productos faltantes.")
        parser.add_argument("--prefix", type=str, default="prov_demo",
                            help="Prefijo para usernames de proveedores (default: prov_demo).")

    def handle(self, *args, **opts):
        n_provs = max(1, opts["providers"])
        per_prov = max(1, opts["per_provider"])
        prefix = opts["prefix"]
        reset  = opts["reset"]

        # regiones a usar
        if opts.get("regions"):
            regiones = [r.strip() for r in opts["regions"].split(",") if r.strip()]
            invalid = [r for r in regiones if r not in CATALOGO]
            if invalid:
                raise CommandError(f"Regiones inválidas: {invalid}.")
        else:
            regiones = list(CATALOGO.keys())
            if not regiones:
                raise CommandError("No hay catálogo de regiones disponible.")

        # categorías
        cat_objs = {
            n: Categoria.objects.get_or_create(
                nombre=n, defaults={"descripcion": d, "activa": True}
            )[0]
            for n, d in CATS.items()
        }

        User = get_user_model()
        total_products = 0
        total_prov = 0

        for i in range(n_provs):
            region = regiones[i % len(regiones)]
            comuna = random.choice(CATALOGO[region])

            uname = f"{prefix}_{i+1}"
            email = f"{uname}@demo.cl"

            u, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "email": email,
                    "tipo_usuario": "proveedor",
                    "is_active": True,
                },
            )
            if created or reset:
                if not u.has_usable_password():
                    u.set_password("12345678")
                u.region = region
                u.comuna = comuna
                u.save()
            else:
                # si ya existía y no pediste reset, no toques su geo
                region = u.region or region
                comuna = u.comuna or comuna

            prov, _ = Proveedor.objects.get_or_create(
                user=u,
                defaults={
                    "tipo_proveedor": "empresa",
                    "nombre_comercial": f"ACME {i+1} {region}",
                    "rut_empresa": f"76.123.{i:03d}-{(i%9)+1}",
                    "giro": "Venta de repuestos",
                },
            )

            # Crear productos por proveedor (SKUs únicos por proveedor)
            base = BASE_ITEMS.copy()
            random.shuffle(base)
            items = base[:per_prov] if per_prov <= len(base) else (base * ((per_prov // len(base)) + 1))[:per_prov]

            creados = 0
            for idx, (nombre, sku, cat_name, precio, stock) in enumerate(items, start=1):
                c = cat_objs[cat_name]
                sku_u = f"{sku}-{slugify(region)[:6]}-{i+1:02d}-{idx:02d}"

                _, made = Producto.objects.get_or_create(
                    codigo_sku=sku_u,
                    defaults={
                        "nombre_producto": nombre,
                        "precio_unitario": precio,
                        "descripcion": f"Producto demo para {region}, comuna {comuna}.",
                        "stock_actual": stock,
                        "stock_minimo": 5,
                        "categoria": c,
                        "proveedor": prov,
                    },
                )
                if made:
                    creados += 1

            total_products += creados
            total_prov += 1
            self.stdout.write(self.style.SUCCESS(
                f"Proveedor {uname} -> {region} / {comuna} | productos nuevos: {creados}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Listo. Proveedores creados/actualizados: {total_prov} | Productos nuevos: {total_products}"
        ))

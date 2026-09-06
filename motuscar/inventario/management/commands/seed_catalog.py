# inventario/management/commands/seed_catalog.py
import random
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from inventario.models import Producto, Categoria
from usuarios.models import User, Proveedor

# --- Regiones/Comunas básicas para prueba (puedes ampliar) ---
REGIONES_COMUNAS = {
    "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué"],
    "Biobío": ["Concepción", "Talcahuano", "San Pedro de la Paz"],
    "Los Lagos": ["Puerto Montt", "Osorno", "Puerto Varas"],
    "Región Metropolitana": ["Santiago", "Providencia", "La Florida"],
}

# --- Familias (prefijo SKU -> nombre y categoría) ---
FAMILIAS = [
    # (prefijo_sku, nombre, categoria)
    ("NEU-2055516", "Neumático 205/55 R16", "Neumáticos"),
    ("NEU-1956515", "Neumático 195/65 R15", "Neumáticos"),
    ("FILT-AIR-STD", "Filtro de aire estándar", "Filtros"),
    ("FILT-FUEL-01", "Filtro de combustible", "Filtros"),
    ("OIL-10W40-4L", "Aceite 10W40 sintético 4L", "Aceites"),
    ("KIT-LED-H7", "Kit LED H7 6000K", "Iluminación"),
]

def code_region(reg: str) -> str:
    """
    Crea un código corto consistente para la región que puedas
    incorporar al SKU. Evita acentos y espacios.
    """
    base = slugify(reg)  # p.ej. "region-metropolitana" -> "region-metropolitana"
    # toma hasta 6 caracteres sin guiones
    return "".join(ch for ch in base if ch.isalnum())[:6] or "rg"

def rut_fake(i: int) -> str:
    # Rut simple válido “de laboratorio” para sortear la validación
    body = f"{10_000_000 + i}"
    dv = "K" if i % 7 == 0 else str((i * 3) % 10)
    return f"{body}-{dv}"

class Command(BaseCommand):
    help = "Siembra catálogo de ejemplo con variantes por región y proveedores."

    def add_arguments(self, parser):
        parser.add_argument(
            "--regions",
            default="Valparaíso,Biobío,Los Lagos,Región Metropolitana",
            help="Lista de regiones separadas por coma.",
        )
        parser.add_argument(
            "--families",
            type=int,
            default=len(FAMILIAS),
            help="Cuántas familias (del listado FAMILIAS) sembrar.",
        )
        parser.add_argument(
            "--per-region",
            type=int,
            default=2,
            help="Cuántas variantes por región crear (1..n proveedores por región).",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra productos, proveedores y usuarios de prueba generados por este comando antes de crear.",
        )
        parser.add_argument(
            "--prefix",
            default="demo",
            help="Prefijo para usuarios/proveedores generados (evita chocar con los reales).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        regions = [r.strip() for r in opts["regions"].split(",") if r.strip()]
        per_region = max(1, int(opts["per_region"]))
        families_to_use = FAMILIAS[: int(opts["families"])]
        prefix = opts["prefix"].lower()

        # 1) Reset opcional
        if opts["reset"]:
            self.stdout.write(self.style.WARNING("Borrando datos de prueba…"))
            # Borra solo lo que tenga el prefijo configurado
            Producto.objects.filter(codigo_sku__icontains=f"-{prefix}-").delete()
            Proveedor.objects.filter(user__username__startswith=f"{prefix}_").delete()
            User.objects.filter(username__startswith=f"{prefix}_").delete()

        # 2) Categorías
        cats = {}
        for _, _, cat_name in families_to_use:
            cats[cat_name], _ = Categoria.objects.get_or_create(
                nombre=cat_name, defaults={"descripcion": f"Categoría {cat_name}"}
            )

        # 3) Crea proveedores “de prueba” por región
        proveedores_por_region = {}
        u_index = 1
        for reg in regions:
            comunas = REGIONES_COMUNAS.get(reg) or ["Centro"]

            provs = []
            for k in range(per_region):
                username = f"{prefix}_{slugify(reg)}_{k+1}"
                email = f"{username}@motuscar.local"
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "first_name": f"Prov {k+1}",
                        "last_name": reg,
                        "region": reg,
                        "comuna": random.choice(comunas),
                        "is_active": True,
                    },
                )
                # Proveedor requiere RUT (empresa o personal)
                prov, _ = Proveedor.objects.get_or_create(
                    user=user,
                    defaults={
                        "tipo_proveedor": "empresa" if k % 2 == 0 else "individual",
                        "nombre_comercial": f"{reg} Parts {k+1}",
                        "rut_empresa": rut_fake(u_index) if k % 2 == 0 else None,
                        "rut_personal": rut_fake(u_index) if k % 2 == 1 else None,
                        "giro": "Venta de repuestos",
                    },
                )
                u_index += 1
                provs.append(prov)
            proveedores_por_region[reg] = provs

        # 4) Genera productos (una fila por proveedor/región = variante)
        creados = []
        random.seed(7331)

        for family_code, family_name, cat_name in families_to_use:
            cat = cats[cat_name]
            for reg in regions:
                provs = proveedores_por_region[reg]
                reg_code = code_region(reg)
                for i, prov in enumerate(provs, start=1):
                    # SKU compuesto: <familia>-<prefijo_comando>-<reg>-<proveedor>-<serie>
                    sku = f"{family_code}-{prefix}-{reg_code}-{i:02d}-{random.randint(1,99):02d}"

                    # Precio base “por familia” con pequeña variación
                    base_price = {
                        "Neumáticos": random.randint(69_990, 119_990),
                        "Filtros": random.randint(7_490, 15_990),
                        "Aceites": random.randint(18_990, 39_990),
                        "Iluminación": random.randint(9_990, 29_990),
                    }.get(cat_name, random.randint(9_990, 49_990))

                    price = base_price + random.choice([0, 1000, 2000, -1000, 3000])
                    stock = random.choice([5, 8, 12, 20, 30, 50])

                    p = Producto(
                        nombre_producto=family_name,
                        codigo_sku=sku,
                        proveedor=prov,
                        categoria=cat,
                        precio_unitario=max(2990, int(price)),
                        descripcion=f"{family_name} — variante {reg} ({prov.user.comuna})",
                        stock_actual=stock,
                        stock_minimo=3,
                    )
                    creados.append(p)

        Producto.objects.bulk_create(creados, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {len(creados)} variantes creadas para {len(families_to_use)} familias "
            f"en {len(regions)} regiones (≈ {per_region} proveedores por región)."
        ))

        self.stdout.write(
            "Recuerda:\n"
            "• El home muestra UNA carta por familia (tu vista ya agrupa por prefijo).\n"
            "• El detalle consolida la disponibilidad por región (usa 'por_region' del view).\n"
        )

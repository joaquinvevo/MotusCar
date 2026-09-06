# ventas/management/commands/seed_geo_cl.py
from django.core.management.base import BaseCommand
from django.db import transaction
from usuarios.models import Proveedor

# Catálogo resumido (suficiente para probar). Puedes ampliar libremente.
CATALOGO = {
    "Arica y Parinacota": ["Arica", "Camarones", "Putre", "General Lagos"],
    "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Pica"],
    "Antofagasta": ["Antofagasta", "Mejillones", "Taltal", "Calama", "San Pedro de Atacama"],
    "Atacama": ["Copiapó", "Caldera", "Vallenar", "Chañaral"],
    "Coquimbo": ["La Serena", "Coquimbo", "Ovalle", "Illapel", "Vicuña"],
    "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué", "Villa Alemana", "San Antonio", "Quillota"],
    "Metropolitana de Santiago": ["Santiago", "Providencia", "Las Condes", "Maipú", "Puente Alto", "La Florida", "Ñuñoa", "Recoleta"],
    "Libertador General Bernardo O'Higgins": ["Rancagua", "Machalí", "San Fernando", "Santa Cruz"],
    "Maule": ["Talca", "Curicó", "Linares", "Cauquenes"],
    "Ñuble": ["Chillán", "Chillán Viejo", "San Carlos", "Coihueco"],
    "Biobío": ["Concepción", "Talcahuano", "San Pedro de la Paz", "Los Ángeles", "Coronel"],
    "La Araucanía": ["Temuco", "Padre Las Casas", "Villarrica", "Pucón"],
    "Los Ríos": ["Valdivia", "La Unión", "Río Bueno", "Panguipulli"],
    "Los Lagos": ["Puerto Montt", "Puerto Varas", "Osorno", "Castro", "Ancud"],
    "Aysén del Gral. C. Ibáñez del Campo": ["Coyhaique", "Aysén", "Chile Chico", "Cochrane"],
    "Magallanes y de la Antártica Chilena": ["Punta Arenas", "Puerto Natales", "Porvenir"],
}

class Command(BaseCommand):
    help = "Asigna Región y Comuna de Chile a los Users vinculados a Proveedores (para probar filtros)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true",
                            help="Limpia region/comuna antes de asignar.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Muestra lo que se haría, sin guardar.")

    @transaction.atomic
    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        reset = opts["reset"]

        proveedores = (Proveedor.objects
                       .select_related("user")
                       .order_by("id"))

        if not proveedores.exists():
            self.stdout.write(self.style.WARNING(
                "No hay Proveedores. Crea al menos 1 Proveedor (con su User) para probar."
            ))
            return

        regiones = list(CATALOGO.keys())
        idx_reg = 0

        total = 0
        for prov in proveedores:
            u = prov.user
            if reset:
                u.region = ""
                u.comuna = ""

            # Si ya tiene datos y no pediste reset, salta
            if u.region and u.comuna and not reset:
                continue

            # Asignación cíclica región/comuna
            region = regiones[idx_reg % len(regiones)]
            comunas = CATALOGO[region]
            comuna = comunas[(idx_reg // len(regiones)) % len(comunas)]

            msg = f"Proveedor #{prov.id} -> {u.username}: {region} / {comuna}"
            if dry:
                self.stdout.write(msg)
            else:
                u.region = region
                u.comuna = comuna
                u.save(update_fields=["region", "comuna"])
                self.stdout.write(self.style.SUCCESS(msg))
            idx_reg += 1
            total += 1

        if dry:
            self.stdout.write(self.style.WARNING(f"[DRY-RUN] Procesados: {total}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Listo. Asignados/actualizados: {total}"))

# motuscar/ventas/views.py

# ... (MANTÉN TUS IMPORTS ARRIBA) ...
from collections import defaultdict
import json
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from inventario.models import Producto, Categoria
from .models import Order, OrderItem, Valoracion

# ... (MANTÉN TUS FUNCIONES base_sku y ventas_home IGUALES) ...
def base_sku(sku: str) -> str:
    parts = (sku or "").split("-")
    return "-".join(parts[:3]) if len(parts) >= 3 else sku

def ventas_home(request):
    # ... (Todo el código de ventas_home igual que antes) ...
    qs = (Producto.objects
          .select_related("categoria", "proveedor", "proveedor__user")
          .filter(stock_actual__gt=0, categoria__activa=True))

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(nombre_producto__icontains=q) | Q(codigo_sku__icontains=q))

    cat = request.GET.get("categoria")
    if cat:
        qs = qs.filter(categoria_id=cat)

    region = (request.GET.get("region") or "").strip()
    comuna = (request.GET.get("comuna") or "").strip()
    if region:
        qs = qs.filter(proveedor__user__region=region)
    if comuna:
        qs = qs.filter(proveedor__user__comuna=comuna)

    pmin = request.GET.get("precio_min")
    if pmin and pmin.isdigit():
        qs = qs.filter(precio_unitario__gte=int(pmin))

    pmax = request.GET.get("precio_max")
    if pmax and pmax.isdigit():
        qs = qs.filter(precio_unitario__lte=int(pmax))

    orden = request.GET.get("orden")
    order_map = {
        "precio_asc": "precio_unitario",
        "precio_desc": "-precio_unitario",
        "nombre_asc": "nombre_producto",
        "nombre_desc": "-nombre_producto",
    }
    if orden in order_map:
        qs = qs.order_by(order_map[orden])
    else:
        qs = qs.order_by("-id_producto")

    if not region and not comuna:
        unique = []
        seen = set()
        for p in qs:
            b = base_sku(p.codigo_sku)
            if b in seen:
                continue
            seen.add(b)
            unique.append(p)
        paginator = Paginator(unique, 12)
    else:
        paginator = Paginator(qs, 12)

    page_obj = paginator.get_page(request.GET.get("page"))

    regiones = (Producto.objects
                .values_list("proveedor__user__region", flat=True)
                .exclude(proveedor__user__region__isnull=True)
                .exclude(proveedor__user__region__exact="")
                .distinct()
                .order_by("proveedor__user__region"))

    comunas_qs = Producto.objects.all()
    if region:
        comunas_qs = comunas_qs.filter(proveedor__user__region=region)
    comunas = (comunas_qs
               .values_list("proveedor__user__comuna", flat=True)
               .exclude(proveedor__user__comuna__isnull=True)
               .exclude(proveedor__user__comuna__exact="")
               .distinct()
               .order_by("proveedor__user__comuna"))

    ctx = {
        "productos": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "categorias": Categoria.objects.filter(activa=True).order_by("nombre"),
        "regiones": list(regiones),
        "comunas": list(comunas),
        "max_precio": (Producto.objects.order_by("-precio_unitario")
                       .values_list("precio_unitario", flat=True).first() or 1000000),
    }
    return render(request, "ventas/index.html", ctx)


# =========================
# DETALLE DE PRODUCTO (MODIFICADO)
# =========================
def producto_detalle(request, sku):
    sku_base = base_sku(sku)

    family_qs = (
        Producto.objects
        .select_related("categoria", "proveedor", "proveedor__user")
        .filter(codigo_sku__startswith=sku_base, categoria__activa=True, stock_actual__gt=0)
        .order_by("precio_unitario")
    )
    if not family_qs.exists():
        family_qs = (
            Producto.objects
            .select_related("categoria", "proveedor", "proveedor__user")
            .filter(codigo_sku__startswith=sku_base, categoria__activa=True)
            .order_by("precio_unitario")
        )
        if not family_qs.exists():
            raise Http404("Producto no encontrado")

    p0 = family_qs.first()

    por_region = defaultdict(list)
    for p in family_qs:
        reg = getattr(getattr(p.proveedor, "user", None), "region", None) or "Sin región"
        com = getattr(getattr(p.proveedor, "user", None), "comuna", "") or ""
        por_region[reg].append({
            "id": p.id_producto,
            "sku": p.codigo_sku,
            "proveedor": getattr(p.proveedor, "nombre_comercial", "Proveedor"),
            "comuna": com,
            "precio": p.precio_unitario,
            "stock": p.stock_actual,
        })

    # === LÓGICA DE VALORACIONES ===
    ha_comprado = False
    mi_valoracion = None # Variable nueva

    if request.user.is_authenticated:
        # 1. ¿Compró?
        ha_comprado = Order.objects.filter(
            user=request.user,
            pagado=True,
            items__sku__startswith=sku_base 
        ).exists()
        
        # 2. ¿Ya opinó? (NUEVO)
        if ha_comprado:
            mi_valoracion = Valoracion.objects.filter(
                usuario=request.user,
                producto__codigo_sku__startswith=sku_base
            ).first()

    valoraciones = Valoracion.objects.filter(producto__codigo_sku__startswith=sku_base).order_by('-creado')

    ctx = {
        "p": p0,
        "sku_base": sku_base,
        "variantes": list(family_qs),
        "por_region": dict(por_region),
        "categorias": Categoria.objects.filter(activa=True).order_by("nombre"),
        "valoraciones": valoraciones,
        "ha_comprado": ha_comprado,
        "mi_valoracion": mi_valoracion, # Pasamos esto al HTML
    }
    return render(request, "ventas/detalle.html", ctx)


# ... (MANTÉN TUS FUNCIONES CARRITO, CHECKOUT, API, WEBPAY IGUALES) ...
def carrito_view(request):
    ctx = {
        "categorias": Categoria.objects.filter(activa=True).order_by("nombre"),
    }
    return render(request, "ventas/carrito.html", ctx)

def checkout_view(request):
    ctx = {
        "categorias": Categoria.objects.filter(activa=True).order_by("nombre"),
    }
    return render(request, "ventas/checkout.html", ctx)

def api_productos(request):
    data = [{
        "id": p.id_producto,
        "nombre": p.nombre_producto,
        "sku": p.codigo_sku,
        "precio": p.precio_unitario,
        "stock": p.stock_actual,
        "categoria": p.categoria.nombre if p.categoria_id else None,
        "proveedor": getattr(p.proveedor, "nombre_comercial", None),
        "region": getattr(getattr(p.proveedor, "user", None), "region", None),
        "comuna": getattr(getattr(p.proveedor, "user", None), "comuna", None),
    } for p in Producto.objects.select_related("categoria", "proveedor__user")]
    return JsonResponse(data, safe=False)

def webpay_init(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")
    cart_json = request.POST.get("cart_json") or "[]"
    total = request.POST.get("order_total") or "0"
    email = (request.POST.get("email") or "").strip()
    nombre_contacto = request.POST.get("nombre") or ""
    direccion = request.POST.get("direccion") or ""
    region = request.POST.get("region") or ""
    comuna = request.POST.get("comuna") or ""
    try:
        cart = json.loads(cart_json)
    except json.JSONDecodeError:
        cart = []
    request.session["buyer_email"] = email
    request.session["mock_order"] = {
        "cart": cart, 
        "total": total,
        "meta": {
            "nombre": nombre_contacto,
            "direccion": direccion,
            "region": region,
            "comuna": comuna
        }
    }
    html = f"""
    <html><body style="font-family:system-ui;padding:20px">
      <h2>Simulador Webpay</h2>
      <p>Total a pagar: <b>${int(float(total)):,}</b></p>
      <p>Items: {len(cart)}</p>
      <div style="display:flex;gap:10px;margin-top:14px">
        <a href="{ reverse('ventas:webpay_sim_ok') }"
           style="padding:10px 14px;background:#16a34a;color:#fff;border-radius:8px;text-decoration:none">Aprobar pago</a>
        <a href="{ reverse('ventas:webpay_sim_fail') }"
           style="padding:10px 14px;background:#b91c1c;color:#fff;border-radius:8px;text-decoration:none">Rechazar pago</a>
      </div>
    </body></html>
    """
    return HttpResponse(html)

def webpay_sim_ok(request):
    order_data = request.session.pop("mock_order", None)
    cart = (order_data or {}).get("cart", [])
    total = (order_data or {}).get("total", "0")
    meta = (order_data or {}).get("meta", {})
    buyer_email = request.session.get("buyer_email")
    total_fmt = f"{int(float(total)):,}"

    if order_data and request.user.is_authenticated:
        nueva_orden = Order.objects.create(
            user=request.user,
            email_contacto=buyer_email,
            nombre_contacto=meta.get("nombre", ""),
            direccion_envio=meta.get("direccion", ""),
            region=meta.get("region", ""),
            comuna=meta.get("comuna", ""),
            pagado=True,
            total_clp=int(float(total))
        )
        for item in cart:
            OrderItem.objects.create(
                order=nueva_orden,
                sku=item.get("sku", ""),
                nombre=item.get("name", "Producto"),
                precio_unitario=int(float(item.get("price", 0))),
                cantidad=int(item.get("qty", 1))
            )

    rows_html_list = []
    for i in cart:
        name = i.get("name", "Producto")
        sku  = i.get("sku", "")
        qty  = int(i.get("qty", 1) or 1)
        price= int(float(i.get("price", 0) or 0))
        rows_html_list.append(
            f"<tr>"
            f"<td><a href='/ventas/p/{sku}/' style='color:#f97316;text-decoration:none;font-weight:bold'>{name}</a></td>"
            f"<td>{sku}</td>"
            f"<td style='text-align:right'>x{qty}</td>"
            f"<td style='text-align:right'>$ {price:,}</td>"
            f"</tr>"
        )
    rows_html = "".join(rows_html_list)

    try:
        if buyer_email:
            msg = EmailMultiAlternatives(
                subject="Tu comprobante de compra – Motuscar",
                body="Gracias por tu compra.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                to=[buyer_email],
            )
            html_email = f"""
              <div style="font-family:system-ui">
                <h3>Comprobante de compra – Motuscar</h3>
                <p>¡Gracias por tu compra!</p>
                <table style="width:100%;border-collapse:collapse">
                  <thead>
                    <tr>
                      <th style="text-align:left">Producto</th>
                      <th>SKU</th>
                      <th style="text-align:right">Cant.</th>
                      <th style="text-align:right">Precio</th>
                    </tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                  <tfoot>
                    <tr>
                      <td colspan="3" style="text-align:right;font-weight:bold">Total</td>
                      <td style="text-align:right;font-weight:bold">$ {total_fmt}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            """
            msg.attach_alternative(html_email, "text/html")
            msg.send(fail_silently=True)
    except Exception:
        pass

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Boleta Electrónica Simulada</title>
      <style>
        body{{ font-family: 'Courier New', Courier, monospace; background: #f3f4f6; padding: 40px; display:flex; justify-content:center; }}
        .boleta{{ background: #fff; padding: 30px; width: 100%; max-width: 450px; border: 1px solid #ddd; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header{{ text-align: center; margin-bottom: 20px; border-bottom: 2px dashed #333; padding-bottom: 15px; }}
        .header h2{{ margin: 0; font-size: 20px; text-transform: uppercase; }}
        .info{{ margin-bottom: 15px; font-size: 14px; }}
        table{{ width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px; }}
        th{{ text-align: left; border-bottom: 1px solid #333; }}
        td{{ padding: 6px 0; }}
        .total{{ border-top: 2px dashed #333; padding-top: 10px; font-size: 18px; font-weight: bold; text-align: right; }}
        .footer{{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; }}
        .btn-back{{ display: block; margin-top: 20px; text-align: center; text-decoration: none; background: #f97316; color: #fff; padding: 10px; border-radius: 6px; font-family: sans-serif; font-weight: bold; }}
      </style>
    </head>
    <body>
      <div class="boleta">
        <div class="header">
          <h2>MotusCar SpA</h2>
          <p>RUT: 76.123.456-K</p>
          <p>Boleta Electrónica Nº {datetime.now().strftime('%Y%m%d%H%M')}</p>
        </div>
        
        <div class="info">
          <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
          <strong>Cliente:</strong> {buyer_email or 'Consumidor Final'}
        </div>

        <table>
          <thead>
            <tr>
              <th>Ítem</th>
              <th style="text-align:right">Valor</th>
            </tr>
          </thead>
          <tbody>
            {rows_html} 
          </tbody>
        </table>

        <div class="total">
          TOTAL: $ {total_fmt}
        </div>
        
        <p style="text-align:center; font-size:12px; margin-top:10px; color:#f97316; font-weight:bold;">
             👇 ¡Haz clic en el producto para calificarlo! 👇
        </p>

        <a href="/ventas/" class="btn-back">Volver a la tienda</a>

        <div class="footer">
          <p>¡Gracias por su preferencia!</p>
          <p>Copia Cliente - Válido como traslado</p>
        </div>
      </div>
    </body>
    </html>
    """
    return HttpResponse(html_response)

def webpay_sim_fail(request):
    request.session.pop("mock_order", None)
    html = """
    <html><body style="font-family:system-ui;padding:20px">
      <h2>Pago rechazado ❌</h2>
      <p>Tu orden no fue procesada.</p>
      <a href="/ventas/carrito/" style="display:inline-block;margin-top:10px">Volver al carrito</a>
    </body></html>
    """
    return HttpResponse(html)

def guardar_valoracion(request, sku):
    if not request.user.is_authenticated or request.method != "POST":
        return redirect('login:login')

    p0 = get_object_or_404(Producto, codigo_sku=sku)
    sku_base = base_sku(sku)
    orden_valida = Order.objects.filter(
        user=request.user, 
        pagado=True, 
        items__sku__startswith=sku_base
    ).first()

    if orden_valida:
        Valoracion.objects.update_or_create(
            usuario=request.user,
            producto=p0,
            orden=orden_valida,
            defaults={
                'puntuacion': request.POST.get('puntuacion'),
                'comentario': request.POST.get('comentario')
            }
        )
    
    return redirect('ventas:detalle', sku=sku)
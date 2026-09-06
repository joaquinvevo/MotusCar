# ventas/urls.py
from django.urls import path
from . import views


app_name = "ventas"

urlpatterns = [
    path("", views.ventas_home, name="home"),
    path("carrito/", views.carrito_view, name="carrito"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("api/productos/", views.api_productos, name="api_productos"),
    path("p/<slug:sku>/", views.producto_detalle, name="detalle"),

    path("webpay/init/", views.webpay_init, name="webpay_init"),
    path("webpay/sim/ok/", views.webpay_sim_ok, name="webpay_sim_ok"),
    path("webpay/sim/fail/", views.webpay_sim_fail, name="webpay_sim_fail"),
    path("valorar/<slug:sku>/", views.guardar_valoracion, name="guardar_valoracion"),
    
]

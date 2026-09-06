from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_selector, name='register_selector'),
    path('register/cliente/', views.register_cliente, name='register_cliente'),
    path('register/mecanico/', views.register_mecanico, name='register_mecanico'),
    path('register/proveedor/', views.register_proveedor, name='register_proveedor'),

    # 🔥 ESTA ES LA IMPORTANTE
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
]

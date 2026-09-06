from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required

User = get_user_model()
# ----------------------------
# LOGIN VIEW
# ----------------------------
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        username = None
        try:
            existing_user = User.objects.get(email=email)
            username = existing_user.username
        except User.DoesNotExist:
            pass  # si no existe, sigue como None

        if username:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('ventas:home')  # <-- cámbialo por tu vista principal
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        else:
            messages.error(request, "No existe ninguna cuenta con ese correo electrónico.")

    return render(request, 'login/login.html')

# ----------------------------
# LOGOUT VIEW
# ----------------------------
def logout_view(request):
    """
    Cierra la sesión y redirige al login.
    """
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('ventas:home')


# ----------------------------
# PROFILE VIEW
# ----------------------------
@login_required
def profile_view(request):
    """
    Muestra el perfil del usuario autenticado.
    """
    return render(request, 'login/profile.html', {'user': request.user})


# ----------------------------
# REGISTER SELECTOR
# ----------------------------
def register_selector(request):
    """
    Página para elegir el tipo de registro: cliente, mecánico o proveedor.
    """
    return render(request, 'login/register_selector.html')


# ----------------------------
# REGISTROS INDIVIDUALES
# ----------------------------
def register_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('login:register_cliente')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe una cuenta con este correo electrónico.")
            return redirect('login:register_cliente')

        username = email.split('@')[0]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        user.first_name = nombre
        user.save()

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect('login:login')

    return render(request, 'login/register_cliente.html')

def register_mecanico(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        especialidad = request.POST.get('especialidad')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('login:register_mecanico')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está en uso.")
            return redirect('login:register_mecanico')

        username = email.split('@')[0]
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = nombre
        user.save()

        messages.success(request, "Cuenta de mecánico creada correctamente.")
        return redirect('login:login')

    return render(request, 'login/register_mecanico.html')

def register_proveedor(request):
    if request.method == 'POST':
        nombre_empresa = request.POST.get('nombre_empresa')
        rut = request.POST.get('rut')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        categoria = request.POST.get('categoria')
        sitio_web = request.POST.get('sitio_web')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('login:register_proveedor')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está en uso.")
            return redirect('login:register_proveedor')

        username = email.split('@')[0]

        # ✅ el campo first_name se pasa directamente aquí
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=nombre_empresa  # ← así evitas el NOT NULL constraint
        )

        # si tienes más campos personalizados (como tipo_usuario, etc.) los puedes agregar
        user.last_name = rut  # opcional
        user.save()

        messages.success(request, "Proveedor registrado exitosamente.")
        return redirect('login:login')

    return render(request, 'login/register_proveedor.html')

#nuevo deff de editar perfil
@login_required
def editar_perfil(request):
    user = request.user

    if request.method == "POST":
        # Datos básicos
        user.first_name = request.POST.get("nombre", user.first_name)
        user.email = request.POST.get("email", user.email)

        # Tipo usuario
        tipo = getattr(user, "tipo", None)

        if tipo == "cliente":
            user.telefono = request.POST.get("telefono")
            user.direccion = request.POST.get("direccion")

        elif tipo == "mecanico":
            user.especialidad = request.POST.get("especialidad")

        elif tipo == "proveedor":
            user.last_name = request.POST.get("rut")
            user.telefono = request.POST.get("telefono")
            user.direccion = request.POST.get("direccion")
            user.categoria = request.POST.get("categoria")
            user.sitio_web = request.POST.get("sitio_web")

        user.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("login:profile")

    return render(request, "login/editar_perfil.html", { "user": user })
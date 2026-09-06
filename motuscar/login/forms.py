from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from usuarios.models import Mecanico, Proveedor, Cliente

User = get_user_model()

# ============================================================
# 🔐 FORMULARIO DE LOGIN (EMAIL)
# ============================================================
from django.contrib.auth import authenticate

class EmailLoginForm(forms.Form):
    """
    Formulario de inicio de sesión usando correo electrónico.
    Compatible con AUTH_USER_MODEL que usa 'email' como USERNAME_FIELD.
    """
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            "placeholder": "Ingresa tu correo",
            "class": "form-control"
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Ingresa tu contraseña",
            "class": "form-control"
        })
    )

    def __init__(self, *args, **kwargs):
        # Django LoginView pasa 'request' al formulario → debemos aceptarlo.
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(self.request, email=email, password=password)
            if not user:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            if not user.is_active:
                raise forms.ValidationError("Tu cuenta está inactiva.")
            cleaned_data["user"] = user
        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get("user")



# ============================================================
# FORMULARIOS DE REGISTRO SEPARADOS
# ============================================================


# ---- Cliente ----
class ClienteRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.tipo_usuario = "cliente"
        if commit:
            user.save()
            Cliente.objects.create(user=user)
        return user


# ---- Mecánico ----
class MecanicoRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    rut = forms.CharField(max_length=12)
    especialidades = forms.CharField(max_length=200)
    experiencia = forms.CharField(max_length=200)
    tiene_taller = forms.BooleanField(required=False)
    direccion_taller = forms.CharField(max_length=255)
    horario_atencion = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.tipo_usuario = "mecanico"
        if commit:
            user.save()
            Mecanico.objects.create(
                user=user,
                rut=self.cleaned_data["rut"],
                especialidades=self.cleaned_data["especialidades"],
                experiencia=self.cleaned_data["experiencia"],
                tiene_taller=self.cleaned_data["tiene_taller"],
                direccion_taller=self.cleaned_data["direccion_taller"],
                horario_atencion=self.cleaned_data["horario_atencion"]
            )
        return user


# ---- Proveedor ----
class ProveedorRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    tipo_proveedor = forms.ChoiceField(choices=Proveedor.TIPO_PROVEEDOR_CHOICES)
    nombre_comercial = forms.CharField(max_length=200)
    rut_empresa = forms.CharField(max_length=12, required=False)
    rut_personal = forms.CharField(max_length=12, required=False)
    giro = forms.CharField(max_length=200, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Las contraseñas no coinciden.")
        if not cleaned.get("rut_empresa") and not cleaned.get("rut_personal"):
            raise ValidationError("Debe ingresar al menos un RUT (empresa o personal).")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.tipo_usuario = "proveedor"
        if commit:
            user.save()
            Proveedor.objects.create(
                user=user,
                tipo_proveedor=self.cleaned_data["tipo_proveedor"],
                nombre_comercial=self.cleaned_data["nombre_comercial"],
                rut_empresa=self.cleaned_data.get("rut_empresa"),
                rut_personal=self.cleaned_data.get("rut_personal"),
                giro=self.cleaned_data.get("giro")
            )
        return user

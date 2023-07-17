from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('verificarCorreo/<str:correo>', views.verificarCorreo, name="verificarCorreo"),
    path('perfil/', views.perfil, name="perfil"),
    path('cambiarContrasena/', views.cambiarContrasena, name="cambiarContrasena"),
    path('verificarNumeroCambio/<str:correo>', views.verificarNumeroCambio, name="verificarNumeroCambio"),
    path('cambiarContrasenaCorrecto/<str:correo>', views.cambiarContrasenaCorrecto, name="cambiarContrasenaCorrecto"),
    path('recortarImagen', views.recortarimagen, name="recortarImagen"),
]
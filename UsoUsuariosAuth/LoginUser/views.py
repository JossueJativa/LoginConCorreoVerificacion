import random
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .models import User
from .verificar import *

# Create your views here.
def index(request):
    return render(request, 'intro/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        phone = request.POST['phone']
        identity = request.POST['identity']
        
        #verificar que la cedula sea valida
        if not verificarCedula(identity):
            return render(request, 'intro/register.html', {
                "message": "La cedula no es valida",
                'username': username,
                'phone': phone,
                'email': email,
            })
        
        #verificar que el usuario no tenga un mismo nombre de usuario
        if User.objects.filter(username=username).exists():
            return render(request, 'intro/register.html', {
                "message": "El nombre de usuario ya existe",
                'phone': phone,
                'identity': identity,
                'email': email,
            })
        
        #verificar que el usuario no tenga un mismo correo
        if User.objects.filter(email=email).exists():
            return render(request, 'intro/register.html', {
                "message": "El correo ya existe",
                'username': username,
                'phone': phone,
                'identity': identity,
            })
        
        #Verificar que el usuario no tenga un mismo numero de identidad
        if User.objects.filter(identity=identity).exists():
            return render(request, 'intro/register.html', {
                "message": "El numero de identidad ya existe",
                    'username': username,
                    'phone': phone,
                    'email': email,
            })
        
        #Verificar que el usuario no tenga el mismo numero de telefono
        if User.objects.filter(phone=phone).exists():
            return render(request, 'intro/register.html', {
                "message": "El numero de telefono ya existe",
                'username': username,
                'identity': identity,
                'email': email,
            })
            
        #verificar que las contraseñas sean iguales
        if password != confirm_password:
            return render(request, 'intro/register.html', {
                "message": "Las contraseñas no coinciden",
                'username': username,
                'phone': phone,
                'identity': identity,
                'email': email,
            })
        
        #Generar un numero ramdom para la confirmacion de correo
        numero = str(random.randint(0000, 9999))

        #enviar correo
        subject = 'Confirmacion de correo'
        message = render_to_string('intro/confirmarCorreo.html', {
            'message': 'Este es el numero de confirmacion de correo',
            'numero': numero,
        })

        email_message = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )
        
        #crear el usuario
        try:
            user = User.objects.create_user(username=username, password=password, email=email, phone=phone, identity=identity, numverification=numero)
            user.save()
        except IntegrityError:
            return render(request, 'intro/register.html', {
                "message": "El usuario ya existe"
            })

        #enviar el correo
        email_message.fail_silently = False
        email_message.send()

        return render(request, 'intro/verificarCorreo.html', {
            'message': "Se ha enviado un correo de confirmacion a su cuenta",
            'correo': email,
            'numero': numero,
        })
    else:
        return render(request, 'intro/register.html')
    
def verificarCorreo(request, correo):
    if request.method == "POST":
        numero = request.POST['numver']

        if User.objects.get(email=correo).numverification == numero:
            User.objects.filter(email=correo).update(is_verified=True)
            login(request, User.objects.get(email=correo))
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(reverse("verificarCorreo", args=[correo,]),{
                'message': "El numero de verificacion es incorrecto",
                'correo': correo,
            })
                    
    else:
        return render(reverse("verificarCorreo", args=[correo,]),{
            'correo': correo,
        })
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = User.objects.get(username=username)
        if user.is_verified == False:
            return render(request, "intro/verificarCorreo.html", {
                "message": "El correo no ha sido verificado",
                'correo': user.email,
            })
        
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "intro/login.html", {
                "message": "Nombre de usuario o contraseña incorrectos.",
                'username': username
            })
    else:
        return render(request, "intro/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def perfil(request):
    if request.method == "POST":
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        username = request.POST['username']
        phone = request.POST['phone']
        identity = request.POST['identity']

        #verificar que la cedula sea valida
        if not verificarCedula(identity):
            return render(request, 'intro/perfil.html', {
                "message": "La cedula no es valida",
                'user': request.user,
            })
        
        #Verificar que no haya el mismo nombre
        if User.objects.filter(username=username):
            if User.objects.get(username=username).id == request.user.id:
                username = username
            else:
                return render(request, 'intro/perfil.html', {
                    "message": "El nombre de usuario ya existe",
                    'user': request.user,
                })
        
        #Verificar numeros de telefono
        if User.objects.filter(phone=phone).exists():
            if User.objects.get(phone=phone).id == request.user.id:
                phone = phone
            else:
                return render(request, 'intro/perfil.html', {
                    "message": "El numero de telefono ya existe",
                    'user': request.user,
                })
            
        #Verificar numero de identidad
        if User.objects.filter(identity=identity).exists():
            if User.objects.get(identity=identity).id == request.user.id:
                identity = identity
            else:
                return render(request, 'intro/perfil.html', {
                    "message": "El numero de identidad ya existe",
                    'user': request.user,
                })

        #Hacer update a la base de datos
        User.objects.filter(id=request.user.id).update(
            first_name=nombre, last_name=apellido, 
            username=username, phone=phone, identity=identity)
        
        user = User.objects.get(id=request.user.id)
        
        return render(request, 'intro/perfil.html', {
            "message": "Se ha actualizado su perfil",
            'user': user,
        })
    else:
        return render(request, 'intro/perfil.html',{
            'user': request.user,
        })
            
def cambiarContrasena(request):
    if request.method == "POST":
        correo = request.POST['email']

        #Enviar un numero aleatorio
        numero = str(random.randint(0000, 9999))

        #Enviar correo
        subject = 'Cambio de contraseña'
        message = render_to_string('intro/confirmarCorreo.html', {
            'message': 'Este es el codigo para cambiar la contraseña',
            'numero': numero,
        })

        email_message = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [correo],
        )

        #enviar el correo
        email_message.fail_silently = False
        email_message.send()

        #Actualizar el numero de verificacion
        User.objects.filter(email=correo).update(numverification=numero)

        return render(request, 'intro/cambiarContrasena.html', {
            'message': "Se ha enviado un correo de confirmacion a su cuenta",
            'correo': correo,
        })
    else:
        return render(request, 'intro/cambiarContrasena.html')
    
def verificarNumeroCambio(request, correo):
    if request.method == "POST":
        numero = request.POST['numver']

        if User.objects.get(email=correo).numverification == numero:
            return render(request, 'intro/VerificadoContrasena.html', {
                'correo': correo,
            })
        else:
            return render(request, 'intro/cambiarContrasena.html', {
                'message': "El numero de verificacion es incorrecto",
                'correo': correo,
            })
    else:
        return render(request, 'intro/VerificadoContrasena.html',{
            'correo': correo,
        })
    
def cambiarContrasenaCorrecto(request, correo):
    if request.method == "POST":
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            return render(request, 'intro/VerificadoContrasena.html', {
                'message': "Las contraseñas no coinciden",
                'correo': correo,
            })
        
        #Actualizar la contraseña
        user = User.objects.get(email=correo)
        user.set_password(password)
        user.save()

        username = user.username

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, 'intro/VerificadoContrasena.html',{
            'correo': correo,
        })
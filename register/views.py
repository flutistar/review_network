import os
import json

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django import forms


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from worker.models import Worker
from .forms import RegisterForm
from .support import get_client_ip, account_activation_token

def register(request):
    if request.method == "POST":
        ip = get_client_ip(request)
        current_site = get_current_site(request)
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            worker = Worker(
                user = user,
                used_ips = ip,
                order_notification = False,
            )
            # worker.save()
            email_subject = 'Activate Your Account'
            message = render_to_string('register/activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            worker.save()
            return HttpResponse('Signup successful')
        else:
            return JsonResponse(dict(form.errors.items()))
                
    else:
        form = RegisterForm()
    return render(request, "register/register.html", {'form': form, 'page': 'Sign Up'})

def signup_success(request):
    return render(request, 'register/signup_success.html')

def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request,user)
        messages.success(request, 'Signup successful')
        return redirect('/dashboard/')
    return HttpResponse('Activation link is invalid!')

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('/dashboard/')
        messages.error(request,'Username or password not correct')
        return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, "register/login.html", {'form': form, 'next': settings.LOGIN_REDIRECT_URL })

def lgoin_superuser_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return HttpResponseRedirect(settings.LOGIN_SUPERUSER_REDIRECT_URL)
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request,user)
                return redirect('/manage/')
            else:
                messages.error(request,'Permission denined')
                return redirect('login')
        else:
            messages.error(request,'Username or password not correct')
        return redirect('login_superuser')
    else:
        form = AuthenticationForm()
    return render(request, "register/login_superuser.html", {'form': form, 'next': settings.LOGIN_SUPERUSER_REDIRECT_URL, 'page': 'Log in' })


def logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

def logout_superuser_view(request):
    logout(request)
    return redirect(settings.SUPREUSER_LOGOUT_REDIRECT_URL)
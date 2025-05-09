from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
import requests
from .forms import RegisterForm
from .models import Account

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            message = render_to_string('verification.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)
            })

            send_mail(
                'Email Verification',
                f'Please verify your mail',
                settings.DEFAULT_FROM_EMAIL,
                (email,),
                html_message=message,
                fail_silently=False,
            )

            messages.success(request,"Regiteration is successfully done.")
            messages.success(request, f'Account created for {first_name} {last_name}! please verify your email to verify.')
            return redirect("account:login")

    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'register.html', context)



def sign_in(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        auth.login(request, user)
        messages.success(request, f'You are now logged in!')
        return redirect('home')

    return render(request,"signin.html")


@login_required(login_url='account:login')
def logout(request):
    auth.logout(request)
    messages.success(request, f'You are now logged out!')
    return redirect('account:login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        print("entered exception ")
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, f'Account has been activated.')
        return redirect('account:login')
    else:
        print("user does not exist")
        messages.error(request, 'Activation link is invalid!')
        return redirect('account:register')


@login_required(login_url="account:login")
def dashboard(request):

    return render(request, 'dashboard.html')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            message = render_to_string('reset_password_validate.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })

            send_mail(
                'Password Reset email',
                f'Please verify your mail',
                settings.DEFAULT_FROM_EMAIL,
                (email,),
                html_message=message,
                fail_silently=False,
            )
            messages.success(request,'password reset email has been sent successfully.')

            return redirect('account:login')

        else:
            messages.error(request, 'Account does not exist!')


    return render(request,'forgotpassword.html')


def reset_password_validate(request,uidb64,token):
    print ("entered function")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        print("entered exception ")
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'please reset your password.')
        return redirect('account:reset_password')
    else:
        messages.error(request, 'this link has been expired.')
        return redirect('account:forgotpassword')



def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            try:
                uid = request.session.get('uid')
                user = Account.objects.get(pk=uid)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successfully.")
                return redirect('account:login')
            except Account.DoesNotExist:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'reset_password.html')

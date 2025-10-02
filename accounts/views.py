#from django.shortcuts import render


from django.shortcuts import render, redirect
from .models import HotelUser
from django.db.models import Q
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
import random
from django.contrib import messages
from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import authenticate, login



def login_page(request): 
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/accounts/login/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/accounts/login/')

        messages.warning(request, "Invalid credentials")
        return redirect('/accounts/login/')
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/accounts/register/')

        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/accounts/register/')


    return render(request, 'register.html')



def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/accounts/login/')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid Token")
    
    
def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(
            email = email)
    if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

    otp =  random.randint(1000 , 9999)
    hotel_user.update(otp =otp)

    sendOTPtoEmail(email , otp)

    return redirect(f'/account/verify-otp/{email}/')
#from django.shortcuts import render


from django.shortcuts import render, redirect
from .models import HotelUser, HotelVendor, Hotel, Ameneties, HotelImages, Hotel
from django.db.models import Q
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
import random
from django.contrib import messages
from django.shortcuts import redirect, HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import generateSlug




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
            return redirect('/')  # redirect to home page

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
        # First try to find a regular user with this token
        hotel_user = HotelUser.objects.filter(email_token=token).first()
        if hotel_user:
            hotel_user.is_verified = True
            hotel_user.save()
            messages.success(request, "Email verified")
            return redirect('/accounts/login/')
        
        # If not found, try to find a vendor with this token
        hotel_vendor = HotelVendor.objects.filter(email_token=token).first()
        if hotel_vendor:
            hotel_vendor.is_verified = True
            hotel_vendor.save()
            messages.success(request, "Vendor email verified")
            return redirect('/accounts/login-vendor/')
            
        # If neither found, return invalid token
        return HttpResponse("Invalid Token")
        
    except Exception as e:
        return HttpResponse("Invalid Token")
    
    
def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(email=email).first()
    if not hotel_user:
        messages.warning(request, "No Account Found.")
        return redirect('/accounts/login/')

    otp = str(random.randint(1000, 9999))  # store as string
    hotel_user.otp = otp
    hotel_user.save()

    sendOTPtoEmail(email, otp)

    return redirect(f'/accounts/verify-otp/{email}/')


def verify_otp(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')
        hotel_user = HotelUser.objects.filter(email=email).first()

        if hotel_user and str(otp) == str(hotel_user.otp):
            hotel_user.otp = None  # clear OTP after use
            hotel_user.save()
            messages.success(request, "Login Success")
            login(request, hotel_user)
            return redirect('/')  # redirect to home page

        messages.warning(request, "Wrong OTP")
        return redirect(f'/accounts/verify-otp/{email}/')

    return render(request, 'verify_otp.html')


def send_otp_vendor(request, email):
    hotel_vendor = HotelVendor.objects.filter(email=email).first()
    if not hotel_vendor:
        messages.warning(request, "No Vendor Account Found.")
        return redirect('/accounts/login-vendor/')

    if not hotel_vendor.is_verified:
        messages.warning(request, "Vendor account not verified")
        return redirect('/accounts/login-vendor/')

    otp = str(random.randint(1000, 9999))  # store as string
    hotel_vendor.otp = otp
    hotel_vendor.save()

    sendOTPtoEmail(email, otp)

    return redirect(f'/accounts/verify-otp-vendor/{email}/')


def verify_otp_vendor(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')
        hotel_vendor = HotelVendor.objects.filter(email=email).first()

        if hotel_vendor and str(otp) == str(hotel_vendor.otp):
            hotel_vendor.otp = None  # clear OTP after use
            hotel_vendor.save()
            messages.success(request, "Login Success")
            login(request, hotel_vendor)
            return redirect('/accounts/dashboard/')  # redirect to vendor dashboard

        messages.warning(request, "Wrong OTP")
        return redirect(f'/accounts/verify-otp-vendor/{email}/')

    return render(request, 'vendor/verify_otp_vendor.html', {'email': email})





def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelVendor.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login-vendor/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/accounts/login-vendor/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            
            login(request , hotel_user)
            return redirect('/accounts/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/accounts/login-vendor/')
    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/accounts/register-vendor/')

        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/accounts/register-vendor/')


    return render(request, 'vendor/register_vendor.html')




@login_required(login_url='login_vendor')
def dashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)



@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(id = request.user.id)

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id = ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()


        messages.success(request, "Hotel Created")
        return redirect('/accounts/add-hotel/')


    ameneties = Ameneties.objects.all()

    return render(request, 'vendor/add_hotel.html', context = {'ameneties' : ameneties})





@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})



@login_required(login_url='login_vendor')
def delete_image(request, id):

    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/accounts/dashboard/')



@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug=slug)
    
    # Check if the current user is the owner of the hotel
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")

    if request.method == "POST":
        # Retrieve updated hotel details from the form
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        
        # Update hotel object with new details
        hotel_obj.hotel_name = hotel_name
        hotel_obj.hotel_description = hotel_description
        hotel_obj.hotel_price = hotel_price
        hotel_obj.hotel_offer_price = hotel_offer_price
        hotel_obj.hotel_location = hotel_location
        hotel_obj.save()
        
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)

    # Retrieve amenities for rendering in the template
    ameneties = Ameneties.objects.all()
    
    # Render the edit_hotel.html template with hotel and amenities as context
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties})



def logout_view(request):
    logout(request)
    messages.success(request, "Logout Success")
    return redirect('/accounts/login/')


def debug_user(request, email):
    """Debug view to check user type"""
    regular_user = HotelUser.objects.filter(email=email).first()
    vendor_user = HotelVendor.objects.filter(email=email).first()
    
    info = f"""
    Email: {email}
    Regular User: {'Yes' if regular_user else 'No'}
    Vendor User: {'Yes' if vendor_user else 'No'}
    """
    
    if regular_user:
        info += f"\nRegular User Verified: {regular_user.is_verified}"
    if vendor_user:
        info += f"\nVendor User Verified: {vendor_user.is_verified}"
    
    return HttpResponse(f"<pre>{info}</pre>")
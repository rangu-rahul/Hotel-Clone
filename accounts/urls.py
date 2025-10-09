from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register, name='register'),
    path('send_otp/<email>/', views.send_otp, name='send_otp'),
    path('verify-otp/<email>/', views.verify_otp, name='verify_otp'),
    

    path('login-vendor/', views.login_vendor, name='login_vendor'),
    path('register-vendor/', views.register_vendor, name='register_vendor'),
    path('send_otp_vendor/<email>/', views.send_otp_vendor, name='send_otp_vendor'),
    path('verify-otp-vendor/<email>/', views.verify_otp_vendor, name='verify_otp_vendor'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('add-hotel/', views.add_hotel, name="add_hotel"),
    path('upload-images/<slug:slug>/', views.upload_images, name="upload_images"),
    path('delete_image/<id>/' , views.delete_image , name="delete_image"),
    path('edit-hotel/<slug:slug>/', views.edit_hotel , name="edit_hotel"),
    path('logout/' , views.logout_view , name="logout_view"),
    path('debug-user/<email>/', views.debug_user, name="debug_user"),




    path('verify-account/<token>/', views.verify_email_token, name="verify_email_token")

]
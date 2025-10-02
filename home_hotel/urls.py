
from django.urls import path
from home_hotel import views


urlpatterns = [
    path('', views.index, name='index'),
   
]
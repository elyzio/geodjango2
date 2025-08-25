from django.urls import path, include
from main.views import *

urlpatterns = [
    path('',Home, name='home'),
    path('home/',Home1, name='home1'),
    path('map/',Map, name='map'),
    path('SignUp/',Register, name='register'),
    path('api/shops/',ShopListApi, name='shop-list-api'),
]
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import RegisterForm
from django.contrib import messages
from shop.models import *
from main.serializers import ShopSerializer
from custom.models import Municipality
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.db.models import Q

# Create your views here.

@api_view(['GET'])
def ShopListApi(request):
    shops = Shop.objects.prefetch_related('shop_images').filter(latitude__isnull=False, longitude__isnull=False, delete_time__isnull=True)
    m_id = request.GET.get('municipality_id')
    banner_kind = request.GET.get('kind_of_banner')
    if m_id:
        shops = shops.filter(municipality__id=m_id, latitude__isnull=False, longitude__isnull=False, delete_time__isnull=True)
    if banner_kind:
        if banner_kind == "No banner information":
            shops = shops.filter(Q(kind_of_banner__isnull=True) | Q(kind_of_banner__iexact="No banner information"))
        else:
            shops = shops.filter(kind_of_banner__iexact=banner_kind)

    serializer = ShopSerializer(shops, many=True, context={'request': request})
    return Response(serializer.data)

def Home(request):
    mun = Municipality.objects.all()
    context = {
        'mun':mun,
        'acHome': 'active',
    }
    return render(request, 'main/back/layout.html', context)

def get_map_config(request):
    return JsonResponse({
        'api_key': settings.GOOGLE_MAPS_API_KEY,
        'default_location': {'lat': -8.552320, 'lng': 125.541782}
    })

@cache_page(60 * 15)
def Home1(request):
    mun = Municipality.objects.all()
    context = {
        'mun':mun,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
        'default_location': {'lat': -8.552320, 'lng': 125.541782},
        'acHome': 'active',
    }
    return render(request, 'main/back/layout2.html', context)

def Map(request):
    return render(request, 'main/map.html')

def Register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect('login')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'title': 'Register',
    }
    return render(request, 'main/auth/registration.html', context)

def custom_404_view(request, exception):
    return render(request, 'main/auth/404.html', status=404)

def custom_403_view(request, exception):
    return render(request, 'main/auth/403.html', status=403)

def custom_500_view(request):
    return render(request, 'main/auth/500.html', status=500)

def custom_503_view(request):
    return render(request, 'main/auth/503.html', status=503)
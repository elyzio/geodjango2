from django.shortcuts import render, redirect
import zipfile
import pandas as pd
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import os
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile, SimpleUploadedFile
from django.contrib.auth.decorators import login_required
from shop.models import *
from shop.forms import *
from custom.models import *
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q


@login_required()
def ShopList(request):
    center = request.GET.get('center', '').strip()
    selected_center = request.GET.get('center')

    mun = Municipality.objects.exclude(name="Estrangeiro").annotate(
        shop_count=Count('center', filter=Q(center__delete_time__isnull=True))
    ).order_by('name')

    shop_count = Shop.objects.filter(delete_time__isnull=True).count()

    # mun = Municipality.objects.filter(exclude='Estrangeiro')
    for m in mun:
        print(f"{m.name}: {m.shop_count} shops via center")

    if center.lower() != "all" and center:
        shop = Shop.objects.filter(center__name__iexact=center, delete_time__isnull=True)
    else:
        shop = Shop.objects.filter(delete_time__isnull=True)

    context = {
        'title': 'Shop List',
        'shops': shop,
        'mun':mun,
        'selected_center': selected_center,
        'shop_count':shop_count,
        "acShop": 'active',
    }
    return render(request, 'shop/list.html', context)

@login_required()
def ShopAdd(request):
    if request.method == 'POST':
        form = ShopAddForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            sh = shop.name
            shop.center_id = request.POST['municipality']
            shop.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Shop {sh} successfully added.')
            return redirect('shop-list')
    else:
        form = ShopAddForm()
    context = {
        'form': form,
        'page': 'add',
        'title': 'Add Shop',
        "acShop": 'active',
    }
    return render(request, 'shop/form.html', context)

@login_required()
def ShopUpdate(request, pk):
    shop = Shop.objects.get(hashed=pk)
    if request.method == 'POST':
        form = ShopAddForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            shop = form.save(commit=False)
            sh = shop.name
            shop.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.info(request, f'Shop {sh} successfully updated.')
            return redirect('shop-list')
    else:
        form = ShopAddForm(instance=shop)
    context = {
        'shop': shop,
        'form': form,
        'page': 'update',
        'title': 'Update Shop',
        "acShop": 'active',
    }
    return render(request, 'shop/form.html', context)

@login_required()
def ShopDetail(request, pk):
    shop = Shop.objects.get(hashed=pk)
    shop_image = ShopImage.objects.filter(shop=shop)
    fixed_image = ShopImage.objects.filter(shop=shop, image_type='FIX', delete_time__isnull=True, is_active=True).order_by('-update_time').first()
    updated_image = ShopImage.objects.filter(shop=shop, image_type='UPDATE', delete_time__isnull=True, is_active=True).order_by('-update_time').first()
    id_image = ShopImage.objects.filter(shop=shop, image_type='ID', delete_time__isnull=True).order_by('-update_time').first()
    context = {
        'shop': shop,
        'title': 'Shop Detail',
        'shop_images':shop_image,
        'fixed_image': fixed_image,
        'update_image': updated_image,
        'id_image': id_image,
        "acShop": 'active',
    }
    return render(request, 'shop/detail.html', context)

@login_required()
def ShopListReport(request):
    shops = Shop.objects.filter(delete_time__isnull=True)
    context = {
        'shops': shops,
        "acShop": 'active',
    }
    return render(request, 'shop/elist.html', context)

@login_required()
def ShopDeleteSoft(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    shop.delete_time = datetime.now()
    sh = shop.name
    shop.save()
    messages.warning(request, f'Shop {sh} successfully deleted.')
    return redirect('shop-list')
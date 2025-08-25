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
def ShopInfoUpdate(request, pk):
    shop = Shop.objects.get(hashed=pk)
    if request.method == 'POST':
        form = ShopInfoForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            shop = form.save(commit=False)
            sh = shop.name
            shop.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.info(request, f'Shop {sh} successfully updated.')
            return redirect('shop-detail', pk)
    else:
        form = ShopInfoForm(instance=shop)
    context = {
        'shop': shop,
        'form': form,
        'page': 'update',
        'title': 'Update Shop Info',
        "acShop": 'active',
    }
    return render(request, 'shop/form_info.html', context)

@login_required()
def ShopLocationUpdate(request, pk):
    shop = Shop.objects.get(hashed=pk)
    if request.method == 'POST':
        form = ShopMapLocationForm(request.POST, instance=shop)
        if form.is_valid():
            map = form.save(commit=False)
            sh = map.sh
            # image.shop_id = shop.id
            map.save()
            messages.info(request, f'Map for Shop {sh} successfully updated.')
            return redirect('shop-detail', pk)
    else:
        form = ShopMapLocationForm(instance=shop)
    context = {
        'shop': shop,
        'form': form,
        'page': 'update',
        'title': 'Update Map Location',
        "acShop": 'active',
    }
    return render(request, 'shop/form_map.html', context)


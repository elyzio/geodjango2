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
def ShopImageList(request):
    # shop = Shop.objects.get(hashed=shop_id)
    shop_images = ShopImage.objects.filter(delete_time__isnull=True).order_by('-update_time')
    context = {
        # 'shop': shop,
        'shop_images': shop_images,
        'title': 'Shop Images List',
        "acShop": 'active',
    }
    return render(request, 'shop/image/list_all.html', context)

def ShopImageAdd(request):
    if request.method == 'POST':
        form = ShopImageForm2(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            # image.shop_id = shop.id
            image.is_active = True
            image.update_time = datetime.now()
            sh = image.shop.name
            images = ShopImage.objects.filter(shop=image.shop, image_type=image.image_type)
            for img in images:
                img.is_active = False
                img.save()
            image.save()
            messages.success(request, f'Shop {sh} successfully added new image.')
            return redirect('shop-image-list-all')
    else:
        form = ShopImageForm2()
    context = {
        # 'shop': shop,
        'form': form,
        'page': 'Add',
        "acShop": 'active',
        'title': 'Add Image Shop',
    }
    return render(request, 'shop/image/form.html', context)


@login_required()
def ShopImageUpdate(request, pk):
    # shop = Shop.objects.get(hashed=shop_id)
    update_image = ShopImage.objects.get(hashed=pk)
    if request.method == 'POST':
        form = ShopImageForm2(request.POST, request.FILES, instance=update_image)
        if form.is_valid():
            image = form.save(commit=False)
            # image.shop_id = shop.id
            image.update_time = datetime.now()
            sh = image.shop.name
            image.save()
            messages.info(request, f'Shop {sh} successfully updated the image.')
            return redirect('shop-list-all')
    else:
        form = ShopImageForm2(instance=update_image)
    context = {
        # 'shop': shop,
        'form': form,
        'page': 'Update',
        "acShop": 'active',
        'title': 'Update Image Shop',
    }
    return render(request, 'shop/image/form.html', context)

@login_required()
def ShopImageDeleteSoft(request,pk):
    img = ShopImage.objects.get(hashed=pk)
    img.delete_time = datetime.now()
    sh = img.shop.name
    img.save()
    messages.warning(request, f'Shop {sh} successfully deleted the image.')
    return redirect('shop-list')

@login_required()
def ShopImageListDetail(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    shop_images = ShopImage.objects.filter(shop=shop, delete_time__isnull=True).order_by('-update_time')
    context = {
        'shop': shop,
        'shop_images': shop_images,
        'title': 'Shop Images List',
        "acShop": 'active',
    }
    return render(request, 'shop/image/list.html', context)

def ShopImageAddDetail(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    if request.method == 'POST':
        form = ShopImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.shop_id = shop.id
            image.is_active = True
            image.update_time = datetime.now()
            sh = image.shop.name
            images = ShopImage.objects.filter(shop=image.shop, image_type=image.image_type).exclude(hashed=image.hashed)
            for img in images:
                img.is_active = False
                img.save()
            image.save()
            
            messages.success(request, f'Shop {sh} successfully added new image.')
            
            return redirect('shop-image-list', shop_id)
    else:
        form = ShopImageForm()
    context = {
        'shop': shop,
        'form': form,
        'page': 'Add',
        'title': 'Add Image Shop',
        "acShop": 'active',
    }
    return render(request, 'shop/image/form.html', context)

def ShopImageAddDetail1(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    image_type = request.GET.get('image_type')
    print(request.method)
    if request.method == 'POST':
        form = ShopImageForm1(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.shop_id = shop.id
            image.is_active = True
            image.image_type = image_type
            image.update_time = datetime.now()
            sh = image.shop.name
            images = ShopImage.objects.filter(shop=image.shop, image_type=image.image_type)
            for img in images:
                img.is_active = False
                img.save()
            image.save()
            
            messages.success(request, f'Shop {sh} successfully added new image.')
            
            return redirect('shop-detail', shop_id)
    else:
        form = ShopImageForm1()
    context = {
        'shop': shop,
        'form': form,
        'page': 'Add',
        'title': 'Add Image for type ' + image_type,
        "acShop": 'active',
    }
    return render(request, 'shop/image/form.html', context)


@login_required()
def ShopImageUpdateDetail(request, shop_id, pk):
    shop = Shop.objects.get(hashed=shop_id)
    update_image = ShopImage.objects.get(hashed=pk, shop=shop)
    if request.method == 'POST':
        form = ShopImageForm2(request.POST, request.FILES, instance=update_image)
        if form.is_valid():
            image = form.save(commit=False)
            # image.shop_id = shop.id
            image.update_time = datetime.now()
            sh = image.shop.name
            image.save()
            messages.info(request, f'Shop {sh} successfully updated the image.')
            return redirect('shop-image-list', shop_id)
    else:
        form = ShopImageForm2(instance=update_image)
    context = {
        'shop': shop,
        'form': form,
        'page': 'Update',
        'title': 'Update Image Shop',
        "acShop": 'active',
    }
    return render(request, 'shop/image/form.html', context)

@login_required()
def ShopImageUpdateDetail1(request, shop_id, pk):
    shop = Shop.objects.get(hashed=shop_id)
    image_type = request.GET.get('image_type')
    update_image = ShopImage.objects.get(hashed=pk, shop=shop)
    if request.method == 'POST':
        form = ShopImageForm1(request.POST, request.FILES, instance=update_image)
        if form.is_valid():
            image = form.save(commit=False)
            # image.shop_id = shop.id
            image.update_time = datetime.now()
            image.image_type = image_type
            sh = image.shop.name
            image.save()
            messages.info(request, f'Shop {sh} successfully updated the image.')
            return redirect('shop-detail', shop_id)
    else:
        form = ShopImageForm1(instance=update_image)
    context = {
        'shop': shop,
        'form': form,
        'page': 'Update',
        'title': 'Update Image for ' + image_type,
        "acShop": 'active',
    }
    return render(request, 'shop/image/form.html', context)



@login_required()
def ShopImageDeleteSoftDetail(request,shop_id, pk):
    img = ShopImage.objects.get(hashed=pk)
    img.delete_time = datetime.now()
    sh = img.shop.name
    img.save()
    messages.warning(request, f'Shop {sh} successfully deleted the image.')
    return redirect('shop-image-list', shop_id)

def ImageUpdatetoFix(request, img_id):
    img = ShopImage.objects.get(hashed=img_id)
    shop = img.shop
    img.image_type = 'FIX'
    img.is_active = True
    img.update_time = datetime.now()
    img.save()
    messages.success(request,f"Change update image to fix for {shop.name}")
    images = ShopImage.objects.filter(shop.shop, image_type='FIX').exclude(hashed=img_id)
    for image in images:
        image.is_active = False
        image.save()
    return redirect('shop-detail', shop.hashed)
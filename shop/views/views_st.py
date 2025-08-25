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
def ShopTrashList(request):
    shop = Shop.objects.filter(delete_time__isnull=False)
    context = {
        'title':'Shop Trash list',
        'shops':shop,
        "acShop": 'active',
    }
    return render(request,'shop/trash/list_trash.html', context)

@login_required()
def ShopTrashRestore(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    image = ShopImage.objects.filter(shop=shop)
    shop.delete_time = None
    sh = shop.name
    shop.save()
    messages.success(request, f'Shop {sh} successfully restored')

    return redirect('shop-trash-list')

@login_required()
def ShopTrashRemoveList(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    images = ShopImage.objects.filter(shop=shop)
    context = {
        'title':'Shop Trash remove list',
        'shop':shop,
        'images':images,
        "acShop": 'active',
    }
    return render(request,'shop/trash/removeP.html', context)

@login_required()
def ShopTrashRemove(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    # image = ShopImage.objects.filter(shop=shop)
    sh = shop.name
    shop.delete()
    messages.warning(request, f'Shop {sh} successfully removed')

    return redirect('shop-trash-list')

@login_required()
def ShopImageTrashListDetail(request, shop_id):
    shop = Shop.objects.get(hashed=shop_id)
    images = ShopImage.objects.filter(shop=shop, delete_time__isnull = False)

    context = {
        'title':'Trash Image list',
        'images':images,
        'shop':shop,
        "acShop": 'active',
    }
    return render(request,'shop/image/trash.html', context)

@login_required()
def ShopImageTrashRestoreDetail(request, shop_id, pk):
    shop = Shop.objects.get(hashed=shop_id)
    image = ShopImage.objects.get(hashed=pk)
    image.delete_time = None
    sh = image.shop.name
    image.save()
    messages.success(request, f'Shop {sh} successfully restore image data')

    return redirect('shop-image-trash-list', shop_id)

@login_required()
def ShopImageTrashRemoveDetail(request, shop_id, pk):
    shop = Shop.objects.get(hashed=shop_id)
    image = ShopImage.objects.get(hashed=pk)
    sh = image.shop.name
    image.delete()
    messages.warning(request, f'Shop {sh} successfully removed image data')

    return redirect('shop-image-trash-list', shop_id)
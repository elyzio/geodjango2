from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Shop, UserShop, ShopImage
from shop.forms import ShopImageForm, ShopInfoForm, ShopMapLocationForm
from users.forms import *


# Create your views here.
# Profile Management
@login_required()
def ProfileUser(request):
    user = request.user

    context = {
        'user':user,
        'title':'Profile',
    }
    return render(request,'users/userProfile.html', context)

@login_required()
def ProfileUserUpdate(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile updated successfully")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    context = {
        'form':form,
        'user':user,
        'title':'Update Profile',
    }
    return render(request,'users/userForm.html', context)







# UserManagement
@login_required()
def UsersManagement(request):
    user = request.user
    shopUser = UserShop.objects.filter(user=user).first()
    shop = Shop.objects.get(id=shopUser.shop.id)
    shop_images = ShopImage.objects.filter(shop=shop).order_by('-is_primary')

    context = {
        'title': 'Shop Management',
        'shop': shop,
        'shop_images': shop_images,
    }
    return render(request, 'users/profiles.html', context)

@login_required()
def UserAddImage(request):
    user = request.user
    shopUser = UserShop.objects.filter(user=user).first()
    shop = Shop.objects.get(id=shopUser.shop.id)

    if request.method == 'POST':
        form = ShopImageForm(request.POST, request.FILES)
        if form.is_valid():
            shop_image = form.save(commit=False)
            shop_image.shop = shop
            shop_image.save()
            return redirect('profile-user')
    else:
        form = ShopImageForm()

    context = {
        'form': form,
        'title': 'Add Image',
    }
    return render(request, 'users/forms_image.html', context)

@login_required()
def UserProfileUpdate(request):
    user = request.user
    shopUser = UserShop.objects.filter(user=user).first()
    shop = Shop.objects.get(id=shopUser.shop.id)
    if request.method == 'POST':
        form = ShopInfoForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('profile-user')
    else:
        form = ShopInfoForm(instance=shop)

    context = {
        'form': form,
        'title': 'Update Profile',
        'shop':shop,
    }
    return render(request, 'users/form_info.html', context)

@login_required()
def UserProfileMap(request):
    user = request.user
    shopUser = UserShop.objects.filter(user=user).first()
    shop = Shop.objects.get(id=shopUser.shop.id)
    if request.method == 'POST':
        form = ShopMapLocationForm(request.POST, instance=shop)
        if form.is_valid():
            form.save()
            return redirect('profile-user')
    else:
        form = ShopMapLocationForm(instance=shop)

    context = {
        'form': form,
        'title': 'Update Profile',
        'shop':shop,
    }
    return render(request, 'users/form_map.html', context)
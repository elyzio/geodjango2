"""geodjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from . import settings
from django.conf.urls.static import static
from main.forms import CustomAuthenticationForm
from django.conf.urls.static import static

handler403 = 'main.views.custom_403_view'
handler404 = 'main.views.custom_404_view'
handler500 = 'main.views.custom_500_view'
handler503 = 'main.views.custom_503_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('main.urls')),
    path('users/',include('users.urls')),
    path('custom/',include('custom.urls')),
    path('shop/',include('shop.urls')),
    path('login/', views.LoginView.as_view(template_name='main/auth/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', views.LogoutView.as_view(template_name='main/auth/logout.html'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG == False:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

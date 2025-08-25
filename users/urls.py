from django.urls import path
from .views import *
from .forms import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('management/', UsersManagement, name='profile-user'),
    path('management/image/add/', UserAddImage, name='add-image-user'),
    path('management/Update/', UserProfileUpdate, name='update-user'),
    path('management/Update/map/', UserProfileMap, name='update-user-map'),

    # Profile
    path('profile/', ProfileUser, name='profile'),
    path('profile/update/', ProfileUserUpdate, name='profile-update'),
    path('profile/password/', auth_views.PasswordChangeView.as_view(
        form_class=UserProfileChangePassword,
        template_name='users/userChangePassword.html',
        success_url='/users/profile/'
    ), name='change_password'),
]

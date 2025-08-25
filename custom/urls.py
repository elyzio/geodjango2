from django.urls import path
from . import views

urlpatterns = [
    path('ajax/load-administrativeposts/', views.load_administrativeposts, name='ajax_load_administrativeposts'),
    path('ajax/load-villages/', views.load_villages, name='ajax_load_villages'),
    path('ajax/load-aldeias/', views.load_aldeias, name='ajax_load_aldeias'),
]
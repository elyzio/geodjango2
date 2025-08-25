from django.shortcuts import render
from django.http import JsonResponse
from .models import AdministrativePost, Village, Aldeia

# Create your views here.

def load_administrativeposts(request):
    municipality_id = request.GET.get('municipality_id')
    administrativeposts = AdministrativePost.objects.filter(municipality_id=municipality_id).order_by('name')
    return JsonResponse(list(administrativeposts.values('id', 'name')), safe=False)

def load_villages(request):
    administrativepost_id = request.GET.get('administrativepost_id')
    villages = Village.objects.filter(administrativepost_id=administrativepost_id).order_by('name')
    return JsonResponse(list(villages.values('id', 'name')), safe=False)

def load_aldeias(request):
    village_id = request.GET.get('village_id')
    aldeias = Aldeia.objects.filter(village_id=village_id).order_by('name')
    return JsonResponse(list(aldeias.values('id', 'name')), safe=False)



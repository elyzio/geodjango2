from django.contrib import admin
from django.utils.html import format_html
from import_export import fields, resources
from import_export.widgets import ManyToManyWidget
from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export import resources
from .models import *

# Resouce
class MunicipalityResource(resources.ModelResource):
    class Meta:
        model = Municipality

class AdministrativePostResource(resources.ModelResource):
    class Meta:
        model = AdministrativePost

class VillageResource(resources.ModelResource):
    class Meta:
        model = Village

class AldeiaResource(resources.ModelResource):
    class Meta:
        model = Aldeia

class ChannelResource(resources.ModelResource):
    class Meta:
        model = Channel

# Register your models here.
@admin.register(Municipality)
class MunicipalityAdmin(ImportExportModelAdmin):
    resource_class = MunicipalityResource
    list_display = ['code', 'name']  # Replace with actual fields from your model
    search_fields = ['name']

@admin.register(AdministrativePost)
class AdministrativePostAdmin(ImportExportModelAdmin):
    resource_class = AdministrativePostResource
    list_display = ['name', 'municipality']  # Assuming `municipality` is a ForeignKey
    search_fields = ['name', 'municipality__name']

@admin.register(Village)
class VillageAdmin(ImportExportModelAdmin):
    resource_class = VillageResource
    list_display = ['name', 'administrativepost']
    search_fields = ['name', 'administrativepost__name']

@admin.register(Aldeia)
class AldeiaAdmin(ImportExportModelAdmin):
    resource_class = AldeiaResource
    list_display = ['name', 'village', 'get_administrative_post', 'get_municipality']
    search_fields = ['name', 'village__name', 'village__administrativepost__name', 'village__administrativepost__municipality__name']

    def get_administrative_post(self, obj):
        return obj.village.administrativepost if obj.village and obj.village.administrativepost else None
    get_administrative_post.short_description = 'Administrative Post'

    def get_municipality(self, obj):
        if obj.village and obj.village.administrativepost:
            return obj.village.administrativepost.municipality
        return None
    get_municipality.short_description = 'Municipality'

@admin.register(Channel)
class ChannelAdmin(ImportExportModelAdmin):
    resource_class = ChannelResource
    list_display = ['name', 'description']

from django.contrib import admin
from django.utils.html import format_html
from import_export import fields, resources
from import_export.widgets import ManyToManyWidget
from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export import resources
from shop.models import *
from custom.models import Municipality, AdministrativePost, Village, Aldeia
# Register your models here.

# admin.site.register(Shop)
# admin.site.register(UserShop)
# admin.site.register(ShopImage)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'municipality', 'administrativepost', 'village', 'aldeia']
    search_fields = ['name', 'owner', 'municipality__name']
    filter_horizontal = ['kind_of_channel']
    readonly_fields = ['hashed']

@admin.register(UserShop)
class UserShopAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop']
    search_fields = ['user__username', 'shop__name']

@admin.register(ShopImage)
class ShopImageAdmin(admin.ModelAdmin):
    list_display = ['shop','image_type','is_active', 'image_preview']
    search_fields = ['shop__name']
    readonly_fields = ['hashed', 'delete_time', 'add_time', 'update_time']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<a href="{}"><img src="{}" height="40" /></a>', obj.image.url, obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

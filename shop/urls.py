from django.urls import path
from shop.views.views_s import *
from shop.views.views_sd import *
from shop.views.views_simg import *
from shop.views.views_simp import *
from shop.views.views_st import *

urlpatterns = [
    path('', ShopList, name='shop-list'),
    path('eprint/', ShopListReport, name='shop-elist'),
    path('create/', ShopAdd, name='shop-add'),
    path('update/<str:pk>/', ShopUpdate, name='shop-update'),
    path('info/<str:pk>/', ShopDetail, name='shop-detail'),
    # path('info/image/add/<str:pk>/', ShopImageAdd, name='shop-add-image'),
    path('info/map/update/<str:pk>/', ShopLocationUpdate, name='shop-update-map'),
    path('info/update/<str:pk>/', ShopInfoUpdate, name='shop-update-info'),
    path('delete/<str:shop_id>/', ShopDeleteSoft, name='shop-delete'),
    path('trash/', ShopTrashList, name='shop-trash-list'),
    path('trash/<str:shop_id>/restore/', ShopTrashRestore, name='shop-trash-restore'),
    path('trash/<str:shop_id>/remove/list/', ShopTrashRemoveList, name='shop-trash-remove-list'),
    path('delete/<str:shop_id>/remove/confirm/', ShopTrashRemove, name='shop-trash-remove'),

    path('import/', import_shops_view1, name='shop-import'),
    path('import/Image/', import_shop_images_view1, name='shop-import-images'),
    path('import/Image/zip/', ShopImageImportZip, name='shop-import-images_zip'),
    # path('import/Image/Preview/', preview_shop_images_view1, name='preview_shop_images_view'),
    # path('import/Image/confirm/', confirm_shop_image_import_view, name='confirm_shop_image_import_view'),

    # Image URLs
    path('update/image/<str:img_id>/toFix/', ImageUpdatetoFix, name='shop-image-update-to-fix'),
    path('image/list/<str:shop_id>/', ShopImageListDetail, name='shop-image-list'),
    path('image/add/<str:shop_id>/', ShopImageAddDetail, name='shop-add-image'),
    path('image/add1/<str:shop_id>/', ShopImageAddDetail1, name='shop-add-image1'),
    path('image/update/<str:shop_id>/<str:pk>/', ShopImageUpdateDetail, name='shop-update-image'),
    path('image/update1/<str:shop_id>/<str:pk>/', ShopImageUpdateDetail1, name='shop-update-image1'),
    path('image/delete/<str:shop_id>/<pk>/', ShopImageDeleteSoftDetail, name='shop-delete-image'),

    path('image/', ShopImageList, name='shop-image-list-all'),
    path('image/create/', ShopImageAdd, name='shop-add-image-all'),
    path('image/change/<pk>/', ShopImageUpdate, name='shop-update-image-all'),
    
    # Image trash
    path('image/trash/<str:shop_id>/', ShopImageTrashListDetail, name='shop-image-trash-list'),
    path('image/trash/<str:shop_id>/restore/<pk>/', ShopImageTrashRestoreDetail, name='shop-image-trash-restore'),
    path('image/trash/<str:shop_id>/remove/<pk>', ShopImageTrashRemoveDetail, name='shop-image-trash-remove'),
]
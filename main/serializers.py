from rest_framework import serializers
from shop.models import Shop, ShopImage, UserShop

class ShopImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopImage
        fields = ['id', 'image','image_type', 'update_time', 'hashed']

class ShopSerializer(serializers.ModelSerializer):
    images  = serializers.SerializerMethodField()
    # images = ShopImageSerializer(many=True, read_only=True)
    # banner_description = serializers.SerializerMethodField()
    kind_of_channel = serializers.SerializerMethodField()
    kind_of_banner = serializers.SerializerMethodField()

    center = serializers.CharField(source='center.name', default=None)
    municipality = serializers.CharField(source='municipality.name', default=None)
    administrativepost = serializers.CharField(source='administrativepost.name', default=None)
    village = serializers.CharField(source='village.name', default=None)
    aldeia = serializers.CharField(source='aldeia.name', default=None)

    class Meta:
        model = Shop
        fields = [
            # 'id', 
            'name', 
            'owner', 
            'contact', 
            'center',
            'municipality', 
            'administrativepost', 
            'village', 
            'aldeia', 
            'latitude', 
            'longitude', 
            'images', 
            # 'banner_description',
            'dimension',
            'kind_of_banner',
            'kind_of_channel',
            'hashed'
            ]

    def get_images(self, obj):
        # images_qs = obj.shop_images.exclude(image_type='ID', delete_time__isnull=False)

        image_fix = obj.shop_images.filter(image_type='FIX', delete_time__isnull=True, is_active=True).order_by('-update_time').first()
        image_update = obj.shop_images.filter(image_type='UPDATE', delete_time__isnull=True, is_active=True).order_by('-update_time').first()
        # request = self.context.get('request')
        images = []
        # for image in images_qs:
        #     # url = image.image
        #     url = image.image.url

        #     images.append({
        #         # 'id': image.id,
        #         'url': url,
        #         'image_type': image.image_type,
        #         'update_time': image.update_time,
        #         'hashed': image.shop.hashed,
        #     })
        if image_fix:
            url_fix = image_fix.image.url
            images.append({
                # 'id': image.id,
                'url': url_fix,
                'image_type': image_fix.image_type.capitalize(),
                'update_time': image_fix.update_time,
                'hashed': image_fix.shop.hashed,
            })
        
        if image_update:
            url_fix = image_update.image.url
            images.append({
                # 'id': image.id,
                'url': url_fix,
                'image_type': image_update.image_type.capitalize(),
                'update_time': image_update.update_time,
                'hashed': image_update.shop.hashed,
            })

        
        return images
    
    def get_kind_of_channel(self, obj):
        return ', '.join([channel.name for channel in obj.kind_of_channel.all()])

    def get_kind_of_banner(self, obj):
        return obj.kind_of_banner or "No banner information"

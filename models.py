from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.contrib.auth.models import User
from custom.models import *
from custom.utils.hashids import encode_id

# Create your models here.

class Shop(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    center = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="center", null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="Municipality", null=True, blank=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, related_name="AdministrativePost", null=True, blank=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="Village", null=True, blank=True)
    aldeia = models.ForeignKey(Aldeia, on_delete=models.CASCADE, related_name="Aldeia", null=True, blank=True)
    kind_of_channel = models.ManyToManyField(Channel, related_name='shops', blank=True)
    dimension = models.CharField(max_length=100, blank=True, null=True)
    CHOICHES = (
        ('Big banner with frame', 'Big banner with frame'),
        ('Small Banner', 'Small Banner'),
    )
    kind_of_banner = models.CharField(max_length=100, blank=True, null=True, choices=CHOICHES)
    add_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deploy_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)
    delete_time = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    hashed = models.CharField(max_length=20, blank=True, editable=False, null=True)

    class Meta:
        db_table = 'shop_shop'
        managed = True

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.hashed:
            self.hashed = encode_id(self.id)
            super().save(update_fields=['hashed'])


    def __str__(self):
        return self.name
    
    def channel_list(self):
        return ", ".join(self.kind_of_channel.values_list("name", flat=True))
    
    def address_full(self):
        parts = [
            str(self.municipality) if self.municipality else '',
            str(self.administrativepost) if self.administrativepost else '',
            str(self.village) if self.village else '',
            str(self.aldeia) if self.aldeia else ''
        ]
        return ", ".join(part for part in parts if part)
    
class UserShop(models.Model):
    # id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ShopOwner', null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'shop_usershop'
        managed = True

@receiver(post_save, sender=User)
def create_client_profile(sender,instance,created, **kwargs):
    if created:
        shop = Shop.objects.create(name=instance.username, contact='', latitude=None, longitude=None)
        UserShop.objects.create(user=instance, shop=shop)

class ShopImage(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_images', null=True)
    image = models.ImageField(upload_to='shop_images/')
    image_type = models.CharField(max_length=50, choices=[('ID', 'ID'), ('FIX', 'FIX'), ('UPDATE', 'UPDATE')], default='OTHER')
    # is_id = models.BooleanField(default=False)
    add_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    delete_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    hashed = models.CharField(max_length=20, blank=True, editable=False, null=True)

    class Meta:
        db_table = 'shop_shopimage'
        managed = True

    def __str__(self):
        return f"{self.shop.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.hashed:
            self.hashed = encode_id(self.id)
            super().save(update_fields=['hashed'])


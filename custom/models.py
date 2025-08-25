from django.db import models

# Create your models here.

class Municipality(models.Model):
    # id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'custom_municipality'
        managed = True

    def __str__(self):
        return self.name
    
class AdministrativePost(models.Model):
    # id = models.IntegerField(primary_key=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'custom_administrativepost'
        managed = True

    def __str__(self):
        return self.name
    
class Village(models.Model):
    # id = models.IntegerField(primary_key=True)
    administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'custom_village'
        managed = True

    def __str__(self):
        return self.name
    
class Aldeia(models.Model):
    # id = models.IntegerField(primary_key=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'custom_aldeia'
        managed = True

    def __str__(self):
        return self.name
    
class Channel(models.Model):
    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'custom_channel'
        managed = True

    def __str__(self):
        return self.name
    
# class Size(models.Model):
#     id = models.IntegerField(primary_key=True)
#     size = models.CharField(max_length=50)

#     class Meta:
#         db_table = 'custom_size'
#         managed = True

#     def __str__(self):
#         return self.size
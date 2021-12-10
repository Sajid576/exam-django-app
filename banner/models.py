from django.db import models

from package.models import Package


class Banner(models.Model):
    banner = models.ImageField(upload_to='bannerImage', null= False) 
    title = models.TextField("Give a Title")
    package = models.OneToOneField(to=Package, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.title


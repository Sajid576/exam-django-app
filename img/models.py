from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class ImageFile(models.Model):
    title = models.CharField(max_length=50)
    images = models.ImageField(upload_to='images')
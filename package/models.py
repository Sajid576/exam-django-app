import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Package(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    defaultDuration = datetime.timedelta(days=30)
    durationDays = models.DurationField(default=defaultDuration)
    fee = models.FloatField()
    examCount = models.IntegerField()
    titleImageUrl = models.ImageField(upload_to ='packageImage',blank=True, null = True)

    def __str__(self):
        return self.name


class User_Package(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    startDate = models.DateField()
    endDate = models.DateField()
    isActive= models.BooleanField(default=False)
    availableExam = models.IntegerField()
    isPinned = models.BooleanField(default=False)
    
    class Meta:
        unique_together=['package','user']

    def __str__(self):
        return str('%s - %s' % (self.user, self.package))
from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    title = models.CharField(max_length=512)
    body = models.TextField(null=True)
    data = models.JSONField(blank=True, null=True)
    image = models.ImageField(upload_to='notification', max_length=512, blank=True, null=True)
    user = models.ManyToManyField(User, through='NotificationUser')

    def __str__(self):
        return self.title

class NotificationUser(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sendTime = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return '%s - %s' %(self.user, self.notification)
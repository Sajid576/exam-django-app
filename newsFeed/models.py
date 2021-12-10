from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User


class NewsFeed(PolymorphicModel):
    title = models.CharField(max_length=255)
    details = models.CharField(max_length=512)

class NewsFeedImage(models.Model):
    news = models.ForeignKey(to=NewsFeed,on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='quesImg')

class ContestNews(NewsFeed):
    winnerAnnounceTime = models.DateTimeField(auto_now=True)
    contestWinnerId = models.ForeignKey(User, on_delete=models.CASCADE)



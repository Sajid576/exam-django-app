from .models import *
from rest_framework import serializers
from rest_framework import permissions, exceptions
from rest_framework.response import Response
from customized_response.response import *
from customized_response.constants import *
from rest_polymorphic.serializers import PolymorphicSerializer


class NewsFeedImageSeriazer(serializers.ModelSerializer):
    class Meta:
        model = NewsFeedImage
        fields = ['image']

class NewsFeedWithImagesSerializer(serializers.ModelSerializer):
    images = NewsFeedImageSeriazer(many= True)
    class Meta:
        model = NewsFeed
        fields = ['id', 'title', 'details', 'images']

    def create(self, validated_data):
        images_list = validated_data.pop('images')
        newsFeedObject = NewsFeed.objects.create(**validated_data)
        for image in images_list:
            NewsFeedImage.objects.create(**image, news= newsFeedObject)
        return newsFeedObject

class NewsFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsFeed
        fields = "__all__"

class ContestResultSerializer(serializers.ModelSerializer):
    images = NewsFeedImageSeriazer(many= True)
    class Meta:
        model = ContestNews
        fields = ['id', 'title', 'details', 'contestWinnerId', 'images']

    def create(self, validated_data):
        images_list = validated_data.pop('images')
        contestNewsObject = ContestNews.objects.create(**validated_data)
        for image in images_list:
            NewsFeedImage.objects.create(**image, news= contestNewsObject)
        return contestNewsObject

class NewsSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        NewsFeed: NewsFeedSerializer,
        ContestNews: ContestResultSerializer
    }
from rest_framework import serializers
from .models import *

class ImageFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageFile
        fields = '__all__'
from django.db.models import fields
from rest_framework import serializers

from .models import *


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Banner
        fields='__all__'
        # depth=1
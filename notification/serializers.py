from rest_framework import serializers
from fcm_django.models import FCMDevice

from .models import *
from customized_response.constants import *


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationUserSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='notification.title')
    body = serializers.ReadOnlyField(source='notification.body')
    data = serializers.ReadOnlyField(source='notification.data')
    image = serializers.ImageField(source='notification.image')

    class Meta:
        model = NotificationUser
        fields = ['title', 'body', 'data', 'image', 'sendTime']


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_id', 'type', 'user']

    def validate(self, attrs):
        reg_id = attrs.get('registration_id')
        user_id = attrs.get('user')
        if FCMDevice.objects.filter(registration_id=reg_id, user_id=user_id).exists():
            raise serializers.ValidationError({'registration_id': DEVICE_REG_ID_EXIST})
        return super().validate(attrs)
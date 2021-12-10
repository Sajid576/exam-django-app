import json
from django.http import request
from django.shortcuts import render
from fcm_django.models import FCMDevice
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, exceptions
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView

from .models import *
from .serializers import *
from customized_response.response import *
from customized_response.constants import *


class IsAdmin(permissions.BasePermission):
    message = error_resp(PERMISSION_DENIED, 'PERMISSION_DENIED')
    
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user:
            return True
        elif not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            raise exceptions.NotAuthenticated(resp)
        else:
            return False


class IsAdminOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user or user.is_authenticated:
            return True
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)


class FCMAddDeviceView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = FCMDeviceSerializer

    def create(self, request, *args):
        serializer = self.get_serializer(data=request.data)
        serializer.initial_data.update({'user':request.user.id})

        if serializer.is_valid():
            serializer.save()
            resp = success_resp(DATA_ADD_SUCCESS, NULL, {})
            return Response(resp, CODE200)

        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class SendBulkNotifications(RetrieveAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAdmin]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        title = serializer.data['title']
        body = serializer.data['body']
        image = serializer.data['image']
        try:
            data = json.loads(serializer.data['data'])
        except:
            data = serializer.data['data']
        
        devices = FCMDevice.objects.all()
        if data is None and image is None: 
            devices.send_message(title=title, body=body)
        elif data is None and image is not None:
            devices.send_message(title=title, body=body, icon=image)
        elif data is not None and image is None:
            devices.send_message(title=title, body=body, data=data)
        else:
            devices.send_message(title=title, body=body, icon=image, data=data)
        
        for device in devices:
            instance.user.add(device.user)
        
        resp = success_resp(NOTIFICATION_SENT_SUCCESS, NULL, {})
        return Response(resp, status=CODE200)


class NotificationlistView(ListAPIView):
    permission_classes = [IsAdminOrAuthenticated]
    serializer_class = NotificationUserSerializer
    
    def get_queryset(self):
        user = self.request.user
        return NotificationUser.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        resp_data = self.list(request, *args, **kwargs).data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)
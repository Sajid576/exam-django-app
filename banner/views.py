from django.shortcuts import render
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView 
from rest_framework import permissions

from .models import *
from .serializers import *


class IsAdminOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser
        if super_user or user.is_authenticated:
            return True
        return False
        # if not user.is_authenticated  :
        #     return False
        # return True

class bannerListView(ListAPIView):
    serializer_class=BannerSerializer
    queryset=Banner.objects.all()
    permission_classes = (IsAdminOrAuthenticated,)

class BannerCreateView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = BannerSerializer        
    queryset = Banner.objects.all()
    permission_classes = (IsAdminOrAuthenticated,)


    # def get(self,request,*args,**kwargs):
    #     if request.user.is_authenticated:
    #         return Response('ok for now')
    #     else:
    #         return Response('not authenticated')

class BannerView(RetrieveUpdateDestroyAPIView):
    serializer_class=BannerSerializer
    queryset=Banner.objects.all()
    lookup_field="id"
    permission_classes = (IsAdminOrAuthenticated,)


class BannnerResponseView(APIView):
    permission_classes = (IsAdminOrAuthenticated,)
    def  get(self,request,*args,**kwargs):
        serializer_class=BannerSerializer
        bannerId=kwargs.get('id',' ')
        package=Banner.objects.get(pk=bannerId)
        print(package.pk)
        return HttpResponseRedirect(f'/api/package/{package.pk}')

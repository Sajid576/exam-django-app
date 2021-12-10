from django.shortcuts import render
from .serializers import *
from customized_response.response import *
from customized_response.constants import *
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework import permissions, exceptions
from rest_framework.response import Response
from drf_nested_forms.parsers import NestedMultiPartParser, NestedJSONParser
from rest_framework.parsers import FormParser


class IsAdminOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user or user.is_authenticated:
            return True
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)  

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_admin = request.user.is_authenticated and request.user.is_superuser
        if not request.method in permissions.SAFE_METHODS or is_admin:
            resp = error_resp(REQ_USER_IS_NOT_ADMIN, 'REQ_USER_IS_NOT_ADMIN')
            raise exceptions.NotAuthenticated(resp) 

class NewsFeedCreateView(CreateAPIView):
    parser_classes = (NestedMultiPartParser, FormParser)
    serializer_class = NewsFeedWithImagesSerializer
    #permission_classes = (IsAdminOrReadOnly,)

class NewsFeedDeleteView(DestroyAPIView):
    serializer_class = NewsFeedSerializer
    queryset = NewsFeed.objects.all()
    #permission_classes = (IsAdminOrReadOnly,)

class NewsFeedView(ListAPIView):
    serializer_class = NewsSerializer
    queryset = NewsFeed.objects.all()
    permission_classes = (IsAdminOrAuthenticated,)
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        resp = success_resp(FETCH_SUCCESS, NULL, response.data)
        return Response(resp, status=CODE200)

class ContestNewsCreateView(CreateAPIView):
    parser_classes = (NestedMultiPartParser, FormParser)
    serializer_class = ContestResultSerializer
    #permission_classes = (IsAdminOrReadOnly,)
    

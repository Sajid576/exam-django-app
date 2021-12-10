from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.generics import *
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework import viewsets

class imageFileView(viewsets.ModelViewSet):
    queryset = ImageFile.objects.all()
    serializer_class = ImageFileSerializer
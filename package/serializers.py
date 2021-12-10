from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *
from exam.serializers import ExamSerializer


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class PackageImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = ['titleImageUrl']

class ExamsPerPackageSerializer(serializers.ModelSerializer):
	exams = ExamSerializer(many=True, read_only=True)
	
	class Meta:
		model = Package
		fields = ['id', 'name', 'description', 'durationDays', 'fee', 
		'examCount', 'titleImageUrl', 'exams']

class User_PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Package
        exclude = ["id", "package", "user"]
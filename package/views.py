from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework import permissions, exceptions
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from rest_framework.views import APIView
from django.utils.timezone import get_current_timezone
from psycopg2 import errorcodes as pg_errorcodes
from django.db import models
from datetime import datetime

from exam.models import *
from .models import *
from .serializers import *
from exam.serializers import *
from customized_response.response import *
from customized_response.constants import *
from authentication.serializers import UserSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_admin = request.user and request.user.is_superuser
        return request.method in permissions.SAFE_METHODS or is_admin

class IsAdminOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user or user.is_authenticated:
            return True
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)  

class IsAdminOrEnrolled(permissions.BasePermission):
    message = error_resp(NOT_ENROLLED, 'NOT_ENROLLED')

    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser
        if not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            raise exceptions.NotAuthenticated(resp)

        packageId = view.kwargs.get('id', 0)
        enrolled = User_Package.objects.filter(
            user_id=user.id, package_id=packageId).exists()
        return super_user or enrolled

class PackageListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        resp_data = {'allPackages' : serializer.data}
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, status=CODE200)


class PackageCreateView(CreateAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()


class PackageDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSerializer
    queryset = Package.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp_data = serializer.data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, status=CODE200)

class ExamsPerPackage(RetrieveAPIView):
    serializer_class = ExamsPerPackageSerializer
    queryset = Package.objects.all()
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp_data = serializer.data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, status=CODE200)


class userPackageView(ListAPIView):
    serializer_class = User_PackageSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            resp_data = {}
            packages = []
            user = User.objects.get(pk=request.user.id)
            queryset = User_Package.objects.filter(user=user).values()

            for elem in queryset:
                package = Package.objects.get(pk=elem['package_id'])
                package_serializer = PackageSerializer(package)                
                new_package_serializer = dict(package_serializer.data)
                new_package_serializer.update(User_PackageSerializer(elem).data)
                packages.append(new_package_serializer)

            resp_data.update({'packages':packages})
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)


class userPinnedPackageView(ListAPIView):
    serializer_class = User_PackageSerializer
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            resp_data = {}
            packages = []
            user= User.objects.get(pk=request.user.id)
            queryset = User_Package.objects.filter(user=user,isPinned=True).values()
            resp_data.update(UserSerializer(user).data)

            for elem in queryset:
                package = Package.objects.get(pk=elem['package_id'])
                package_serializer = PackageSerializer(package)                
                new_package_serializer = dict(package_serializer.data)
                new_package_serializer.update(User_PackageSerializer(elem).data)
                packages.append(new_package_serializer)

            resp_data.update({'packages':packages})
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)

class userRecommendedPackageView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    def get(self, request, *args, **kwargs):
        userPackages = User_Package.objects.filter(user_id = self.request.user.id).values_list('package_id', flat=True)            
        packages =  Package.objects.exclude(id__in=userPackages)
        serialized_packages = []
        for package in packages:
            serialized_packages.append(PackageSerializer(package).data)
        resp_data = {}
        resp_data.update({"packages": serialized_packages})
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, status=CODE200)


class enrollUserView(APIView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            packageId = kwargs.get('packageId')
            package = Package.objects.get(pk= packageId)
            startDate = datetime.today()
            endDate = startDate + package.durationDays
            availableExam  = package.examCount
            user = User.objects.get(pk= request.user.id)
            try:
                userPackage = User_Package(package=package, user=user ,startDate=startDate, endDate=endDate, isActive=True, availableExam=availableExam)
                userPackage.save()
            except IntegrityError as ex:
                if ex.__cause__.pgcode == pg_errorcodes.UNIQUE_VIOLATION:
                    resp = error_resp(PACK_ENROLLED_PREV, 'PACK_ENROLLED_PREV')
                    return Response(resp, status=CODE400)
            
            resp = success_resp(PACK_ENROLLED, NULL, {})
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)



    '''
     def post(self, request):
        super()
        packageId = request.POST.get('pk')
        pname =  request.POST.get('name')
        pdes =  request.POST.get('description')
        ddays =  request.POST.get('duration_days')
        fee =  request.POST.get('fee')
        title_image_url =  request.POST.get('title_image_url')
        startDate = datetime.today().strftime("%d/%m/%Y")
        endDate = datetime.today().strftime("%d/%m/%Y")
        availableExam = request.POST['exam_count']
        isActive = request.POST.get('is_Active')
        isPaid = request.POST.get('is_paid')
        print('debug')
        if (isPaid == 'true'):
            isPaid = True
        PackageObj = Package(name=pname,description=pdes,duration_days=ddays,fee=fee,is_paid=isPaid,exam_count=availableExam,title_image_url=title_image_url)
        PackageObj.save()
        print(PackageObj.pk)
        tz = get_current_timezone()
        startDate = tz.localize(datetime.strptime(startDate.__str__(), '%d/%m/%Y'))
        endDate = tz.localize(datetime.strptime(endDate.__str__(), '%d/%m/%Y'))
        print(endDate)
        userPackage = User_Package(package=Package.objects.get(pk = PackageObj.pk), start_date=startDate, end_date=endDate, is_Active=True,available_exam=availableExam)
        userPackage.save()
        return Response('')
'''

class doPinPackageView(APIView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            packageId = kwargs.get('packageId')
            package = Package.objects.get(pk= packageId)
            user= User.objects.get(pk=request.user.id)
            userPackage = User_Package.objects.filter(user=user,package=package).first()
            userPackage.isPinned = True
            userPackage.save()
            resp = success_resp(PACK_PIN, NULL, {}) 
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)

class doUnPinPackageView(APIView):
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            packageId = kwargs.get('packageId')
            package = Package.objects.get(pk= packageId)
            user= User.objects.get(pk=request.user.id)
            userPackage = User_Package.objects.filter(user=user,package=package).first()
            userPackage.isPinned = False
            userPackage.save()
            resp = success_resp(PACK_UNPIN, NULL, {})
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)


class nextExamInPackage(APIView):
    permission_classes = (IsAdminOrEnrolled,)

    def get(self, request, *args, **kwargs):
        resp_data = {}
        packageId = kwargs.get('id')
        package = Package.objects.get(pk=packageId)
        userPackage = User_Package.objects.all().get(package_id=packageId, user=request.user)
        exams = Exam.objects.filter(package_id=packageId)
        userExams = UserExam.objects.filter(
            userId_id=request.user.id).values_list('examId_id', flat=True)            
        exams = exams.exclude(id__in=userExams)
        
        if package.fee != 0:
            viewAble=False
            retakeAble=True
        else:
            viewAble=True
            retakeAble=True
        
        for newExam in exams:
            userExam = UserExam(examId_id=newExam.id, userId_id=request.user.id, 
            examDate=datetime.now(UTC), participationCount=1, 
            consumedTime=timedelta(hours=0, minutes=0, seconds=0),
            obtainedMarks=0, totalCorrectedQuestions=0, totalIncorrectedQuestions=0,
            viewAble=viewAble, retakeAble=retakeAble)
            userExam.save()

            resp_data.update(QuestionsPerExamSerializer(newExam).data)
            availableExam = userPackage.availableExam -1
            userPackage.availableExam = availableExam
            userPackage.save()
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(NO_EXAM_AVAILABLE_IN_PACKAGE, 'NO_EXAM_AVAILABLE_IN_PACKAGE')
        return Response(resp, status=CODE400)


class nextQuizExamInPackage(APIView):
    permission_classes = (IsAdminOrEnrolled,)

    def get(self, request, *args, **kwargs):
        resp_data = {}
        packageId = kwargs.get('id')
        package = Package.objects.get(pk=packageId)
        userPackage = User_Package.objects.all().get(package_id = packageId, user = request.user)
        exams = Exam.objects.filter(package_id=packageId)
        userExams = UserExam.objects.filter(
            userId_id=request.user.id).values_list('examId_id', flat=True)            
        exams = exams.exclude(id__in=userExams)
        
        if package.fee != 0:
            viewAble=False
            retakeAble=True
        else:
            viewAble=True
            retakeAble=True
        
        for newExam in exams:
            userExam = UserExam(examId_id=newExam.id, userId_id=request.user.id, 
            examDate=datetime.now(UTC), participationCount=1, 
            consumedTime=timedelta(hours=0, minutes=0, seconds=0),
            obtainedMarks=0, totalCorrectedQuestions=0, totalIncorrectedQuestions=0,
            viewAble=viewAble, retakeAble=retakeAble)
            userExam.save()

            resp_data.update(QuestionsPerExamSerializerWithCorrectAnswer(newExam).data)
            availableExam = userPackage.availableExam -1
            userPackage.availableExam = availableExam
            userPackage.save()
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(NO_EXAM_AVAILABLE_IN_PACKAGE, 'NO_EXAM_AVAILABLE_IN_PACKAGE')
        return Response(resp, status=CODE400)

import os
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from rest_framework.response import Response
from datetime import date, datetime, timedelta
from psycopg2 import errorcodes as pg_errorcodes
from rest_framework import permissions, exceptions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView

from .models import *
from .serializers import *
from customized_response.response import *
from customized_response.constants import *
from newsFeed.models import ContestNews
from authentication.serializers import UserSerializer


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True

        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)


class DesignContestListView(ListAPIView):
	serializer_class = DesignContestSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		today = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		return DesignContest.objects.filter(startDate__lte = today, endDate__gte = today)
	
	def list(self, request, *args, **kwargs):
		resp_data = {}
		queryset = self.filter_queryset(self.get_queryset())
		page = self.paginate_queryset(queryset)

		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		for contest in serializer.data:
			try:
				ContestData.objects.get(user=request.user, designContest_id=contest['id'])
				contest.update({'submitted': True})
			except:
				contest.update({'submitted': False})

		resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
		return Response(resp, status=CODE200)


class DesignContestDetailView(RetrieveAPIView):
	serializer_class = DesignContestSerializer
	queryset = DesignContest.objects.all()
	lookup_field = 'id'
	permission_classes = [IsAuthenticated]

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.get_serializer(instance)
		resp_data = serializer.data

		try:
			ContestData.objects.get(user=request.user, designContest_id=kwargs.get('id'))
			resp_data.update({'submitted': True})
		except:
			resp_data.update({'submitted': False})
		
		resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
		return Response(resp, status=CODE200)


class ContestDataSubmitView(APIView):
	parser_classes = (JSONParser, FormParser, MultiPartParser)
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		designContestId = kwargs.get('id')
		designContest = DesignContest.objects.get(pk=designContestId)
		serializer = ContestDataSerializer(data=request.data, 
			context={'request':request, 'contest':designContest})

		today = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
		if  today <= designContest.endDate.strftime("%Y-%m-%dT%H:%M:%SZ"): 
			if serializer.is_valid():
				image_url_list = serializer.save()

				resp_data = {}
				user= User.objects.get(pk=request.user.id)
				resp_data.update(UserSerializer(user).data)

				resp_data.update({'images':image_url_list})
				resp = success_resp(DATA_SUBMIT_SUCCESS, NULL, resp_data)
				return Response(resp, status=CODE200)

			resp = error_check(serializer.errors)       
			return Response(resp, status=CODE400)
		
		resp = error_resp(TIME_UP, 'TIME_UP')
		return Response(resp, status=CODE400)


class ContestDataRetrieveView(RetrieveAPIView):
	permission_classes = [IsAuthenticated]
	
	def retrieve(self, request, *args, **kwargs):
		try:
			userId = self.request.user.id
			designContestId = kwargs.get('id')
			contest_data = ContestData.objects.get(user_id=userId,
				designContest_id=designContestId)
			
			resp_data = {}
			user = User.objects.get(pk=userId)
			resp_data.update(UserSerializer(user).data)
	
			images = []
			img_set = ContestImage.objects.filter(contestData_id=contest_data.id)
			for img in img_set:
				img_serializer = ContestImageSerializer(img, 
					context={'request':self.request})
				images.append(img_serializer.data)

			resp_data.update({'images':images})
			resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
			return Response(resp, status=CODE200)

		except:
			resp = error_resp(DATA_NOT_FOUND, 'DATA_NOT_FOUND')
			raise exceptions.NotFound(resp)


class FileRemoveView(DestroyAPIView):
	permission_classes = [IsAuthenticated]

	def destroy(self, request, *args, **kwargs):
		userId = self.request.user.id
		designContestId = kwargs.get('id')
		img_del = request.data['removedImages']

		try:
			contest_data = ContestData.objects.get(user_id=userId,
					designContest_id=designContestId)
			
			img_set = ContestImage.objects.filter(contestData_id=contest_data.id)
			for img in img_set:
				img_serializer = ContestImageSerializer(img, context={'request':self.request})
				if img_del in img_serializer.data['image']:
					self.perform_destroy(img)
					resp = success_resp(RESOURCE_DEL_SUCCESS, NULL, {})
					return Response(resp, status=CODE200)
			
			resp = error_resp(IMAGE_NOT_FOUND, 'IMAGE_NOT_FOUND')
			return Response(resp, status=CODE404)
		
		except:
			resp = error_resp(DATA_NOT_FOUND, 'DATA_NOT_FOUND')
			raise exceptions.NotFound(resp)


class UserContestPerformanceView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		resp_data = {}
		weeks = []
		week_no = 1
		start_date = START_DATE
		end_date = start_date + timedelta(days=6)
		today = datetime.utcnow().date()

		while start_date <= today:
			weekly_result = {}
			contests = ContestData.objects.filter(user_id=request.user.id, 
            submitTime__date__gte=start_date, submitTime__date__lte=end_date)
            
			newsfeeds = ContestNews.objects.filter(contestWinnerId_id=request.user.id,
			winnerAnnounceTime__date__gte=start_date, winnerAnnounceTime__date__lte=end_date)
			
			if len(contests) == 0 and len(newsfeeds) == 0: 
				start_date = end_date + timedelta(days=1)
				end_date = start_date + timedelta(days=6)
				continue
			
			contest_participation_count_per_week = 0
			contest_win_count_per_week = 0
			
			for contest in contests:
				contest_participation_count_per_week += 1
			    
			for newsfeed in newsfeeds:
				contest_win_count_per_week += 1	
			
			weekly_result["dateRange"] = str(start_date) + " to " + str(end_date)
			weekly_result["contestParticipationCount"] = contest_participation_count_per_week
			weekly_result["contestWinCount"] = contest_win_count_per_week
			weeks.append(weekly_result)  
			
			week_no += 1
			start_date = end_date + timedelta(days=1)
			end_date = start_date + timedelta(days=6)
		
		resp_data["weeks"] = weeks[::-1]
		resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
		return Response(resp, status=CODE200)


'''
class IsAdminOrEnrolled(permissions.BasePermission):
    message = error_resp(NOT_ENROLLED, 'NOT_ENROLLED')

    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser
        if not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            raise exceptions.NotAuthenticated(resp)

        contestId = view.kwargs.get('id', 0)
        enrolled = ContestEnroll.objects.filter(
            user_id=user.id, designContest_id=contestId).exists()
        return super_user or enrolled

class EnrollUserView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request, *args, **kwargs):
		designContestId = kwargs.get('designContestId')
		designContest = DesignContest.objects.get(pk=designContestId)
		user = User.objects.get(pk=request.user.id)

		if datetime.date.today() <= designContest.endDate.date():
			try:
				enroll = ContestEnroll(user=user, designContest=designContest)
				enroll.save()
				resp = success_resp(CONTEST_ENROLL, NULL, {})
				return Response(resp, status=CODE200)
			
			except IntegrityError as ex:
				if ex.__cause__.pgcode == pg_errorcodes.UNIQUE_VIOLATION:
					resp = error_resp(CONTEST_ENROLLED_PREV, 'CONTEST_ENROLLED_PREV')
					return Response(resp, status=CODE400)			
		
		resp = error_resp(ENROLL_TIME_UP, 'ENROLL_TIME_UP')
		return Response(resp, status=CODE400)

class ContestDataSubmitView(CreateAPIView):
	serializer_class = ContestDataSerializer
	parser_classes = (JSONParser, FormParser, MultiPartParser)
	permission_classes = [IsAuthenticated]

	def post(self, request, **kwargs):
		designContestId = kwargs.get('id')
		designContest = DesignContest.objects.get(pk=designContestId)
		serializer = ContestDataSerializer(data=request.data, 
			context={'request':request, 'contest':designContest})

		if datetime.date.today() <= designContest.endDate.date():
			if serializer.is_valid():
				try:
					image_url_list = serializer.save()

					resp_data = {}
					user= User.objects.get(pk=request.user.id)
					resp_data.update(UserSerializer(user).data)
					resp_data.update(serializer.data)

					images = []
					for image_url in image_url_list:
						images.append(image_url['image'])

					resp_data.update({'images':images})
					resp = success_resp(DATA_SUBMIT_SUCCESS, NULL, resp_data)
					return Response(resp, status=CODE201)			

				except IntegrityError as ex:
					if ex.__cause__.pgcode == pg_errorcodes.UNIQUE_VIOLATION:
						resp = error_resp(DATA_SUBMIT_PREV, 'DATA_SUBMIT_PREV')
						return Response(resp, status=CODE400)
			
			resp = error_check(serializer.errors)       
			return Response(resp, status=CODE400)
		
		resp = error_resp(TIME_UP, 'TIME_UP')
		return Response(resp, status=CODE400)
'''
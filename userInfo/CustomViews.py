from rest_framework import status
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from .serializers import *
from customized_response.response import *
from customized_response.constants import *

class CustomCreateUpdateView(GenericAPIView):

    myClass= None
    def post(self, request, **kwargs):
        
        # check if user present in the request
        user = request.user
        if not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            return Response(resp, status=CODE401)

        mydictionary={}
        mydictionary['user']=user
        for field in request.data:
            if (field=='city'):
                mydictionary[field]=Cities.objects.get(id=request.data[field])
                continue
            if(field=='user' or '_at' in field):
                continue
            mydictionary[field]=request.data[field]     

        obj = self.myClass(**mydictionary)

        for field in obj.__dict__:
            if(field=='id' or field=='user_id'):
                continue
            if(not type(obj.__dict__[field]) == bool or '_at' in field):
                if (not obj.__dict__[field]):
                    resp = error_resp(INVALID_REQ, 'INVALID_REQ')
                    return Response(resp, status=CODE400)


        try:
            obj.save()
        except IntegrityError as identifier:
            return Response("Data already Exists", status=status.HTTP_200_OK)
        resp = success_resp(PROFILE_CREATE_SUCCESS, NULL, {})
        return Response(resp, status=CODE200)

    def put(self, request, **kwargs):
        
        # check if user present in the request
        user = request.user
        if not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            return Response(resp, status=CODE401)


        try:
            obj = self.myClass.objects.get(user=user)
        except ObjectDoesNotExist as identifier:
            resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
            return Response(resp, status=CODE404)

        #loops though request.data and address object and sets them accordingly
        #skips loop if field is equal to user or datefield or empty
        for field in request.data:
                if(field=='user' or '_at' in field or not request.data[field]):
                    continue
                obj.__dict__[field]=request.data[field]

        obj.user = user   

        try:
            obj.save()
        except IntegrityError as identifier:
            return Response("Data already Exists", status=status.HTTP_200_OK)

        return Response(PROFILE_UPDATE_SUCCESS, status=CODE200)
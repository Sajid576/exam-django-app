from django import http
from datetime import date
from rest_framework import status
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import permissions, exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView

from .models import *
from .serializers import *
from .CustomViews import *
from customized_response.response import *
from customized_response.constants import *
from authentication.serializers import UserSerializer
from allauth.socialaccount.models import SocialAccount


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


def calculate_completeness(dict_items):
    count = 0
    for k,v in dict_items:
        if v != None and v != "":
            count += 1
    return (count / len(dict_items))*100


def resolve_FK(model, serializer, field):    
    if serializer.initial_data[field] is not None and serializer.initial_data[field] != '':
        try:
            instance = model.objects.get(name__iexact=serializer.initial_data[field])
        except:
            instance = model.objects.create(name=serializer.initial_data[field])

        serializer.initial_data.update({field:instance.id})

def resolve_FK2(model, fieldVal):    
    try:
        instance = model.objects.get(name__iexact=fieldVal)
    except:
        instance = model.objects.create(name=fieldVal)
    return instance.id

def resolve_choices(choices, serializer, field):
    if serializer.initial_data[field] is not None:
        for choice in choices:
            if choice[1].lower() == serializer.initial_data[field].lower():
                serializer.initial_data.update({field:choice[0]})
                break


def getChoice(data, choices):
    data = data.lower()
    for choice in choices:
        if choice[1].lower() == data:
            return choice[0]
            break
    return -1


def format_str(str):
    if str != None and str != '':
        return str + ', '
    else:
        return ''


class ProfileUpdateView(UpdateAPIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAdminOrAuthenticated,)

    def update(self, request):
        context = {'user_id': request.user.id}
        serializer = ProfileSerializer(data=request.data, context=context)
        context['remove'] = request.data['remove']
        
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True        
        
        resolve_FK(Nationality, serializer, 'nationality')
        resolve_choices(RELIGIONS, serializer, 'religion')
        resolve_choices(CITIZENSHIP_STATUS, serializer, 'citizenshipStatus')
        
        if serializer.is_valid():
            if serializer.initial_data['dateOfBirth'] == '':
                serializer.validated_data['dateOfBirth'] = None

            dateOfBirth = serializer.validated_data['dateOfBirth'] 
            if dateOfBirth is not None and dateOfBirth > date.today():
                resp = error_resp(INVALID_DATE, 'INVALID_DATE')
                return Response(resp, status=CODE400)

            resp_data = {}
            user = User.objects.get(id=request.user.id)
            user_serializer = UserSerializer(user).data
            resp_data.update(user_serializer)
            
            serializer.update()

            profile = Profile.objects.get(user_id=request.user.id)
            profile_serializer = ProfileRetrieveSerializer(profile,
            context={'request': request}).data
            resp_data.update(profile_serializer)
            
            if resp_data['image'] is None:
                resp_data['image'] = ""
            
            resp = success_resp(PROFILE_UPDATE_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)

        resp = error_check(serializer.errors)
        return Response(resp, status=CODE400)


class ProfileRetrieveView(RetrieveAPIView):
    serializer_class = ProfileRetrieveSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsAdminOrAuthenticated,)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            instance = get_object_or_404(queryset, user=self.request.user)
            return instance
        except:
            resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
            raise exceptions.NotFound(resp)

    def retrieve(self, request, *args, **kwargs):
        resp_data = {}

        user = User.objects.get(id=request.user.id)
        user_serializer = UserSerializer(user).data
        resp_data.update(user_serializer)
        
        instance = self.get_object()
        profile_serializer = self.get_serializer(instance).data
        resp_data.update(profile_serializer)
        
        if resp_data['image'] is None:
            resp_data['image'] = ""
        #if resp_data['dateOfBirth'] is None:
        #    resp_data['dateOfBirth'] = ""

        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, status=CODE200)


class AddressCreateView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAdminOrAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {'user_id': request.user.id}
        
        serializer = AddressSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True

        resolve_FK(Countries, serializer, 'country')
        resolve_FK(Division, serializer, 'division')
        resolve_FK(Districts, serializer, 'district')
        resolve_FK(Thana, serializer, 'thana')
        resolve_FK(Village, serializer, 'village')
        resolve_FK(PostOffice, serializer, 'postOffice')
        
        if serializer.is_valid():
            serializer.save()
            resp = success_resp(ADDRESS_UPDATE_SUCCESS, NULL, {})
            return Response(resp, CODE200)   

        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class AddressRetrieveView(APIView):
    permission_classes = (IsAdminOrAuthenticated,)

    def get(self, request, *args, **kwargs):
        empty_data = {
            "roadNo": "",
            "isPermanentAddress": "",
            "sameAsPresentAddress": "",
            "country": "",
            "division": "",
            "district": "",
            "thana": "",
            "village": "",
            "postOffice": ""
        }
        resp_data = {}

        user = User.objects.get(id=request.user.id)
        user_serializer = UserSerializer(user).data
        resp_data.update(user_serializer)
        
        try:
            instance = Address.objects.get(user_id=request.user.id, 
            isPermanentAddress=True)
            serializer = AddressRetrieveSerializer(instance)
            resp_data['permanentAddress'] = serializer.data
        except:
            resp_data['permanentAddress'] = empty_data
        
        try:
            instance = Address.objects.get(user_id=request.user.id, 
            isPermanentAddress=False)
            serializer = AddressRetrieveSerializer(instance)
            resp_data['presentAddress'] = serializer.data
        except: 
            resp_data['presentAddress'] = empty_data 
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)

        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, status=CODE200)


class LandingProfileView(APIView):
    permission_classes = (IsAdminOrAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        resp_data = {}
        
        #personalInfo
        personal_data = {}
        
        try:
            profile = Profile.objects.get(user_id=request.user.id)
            profile_serializer = PersonalInfoSerializer(profile,
            context={'request': request})
            
            if profile_serializer.data['firstName'] != None:
                full_name = profile_serializer.data['firstName'] + ' '
            else:
                full_name = ''
            if profile_serializer.data['lastName'] != None:
                full_name += profile_serializer.data['lastName'] 
            else:
                full_name += ''
            if full_name == '':
                full_name += request.user.username
            personal_data['name'] = full_name.strip()
            personal_data['nationality'] = profile_serializer.data['nationality']
            try:
                social = SocialAccount.objects.get(user=request.user)
                personal_data['image'] = social.extra_data['picture']
            except:
                personal_data['image'] = profile_serializer.data['image']
            
            serializer = ProfileRetrieveSerializer(profile)
            personal_data['completeness'] = calculate_completeness(serializer.data.items())
            
            resp_data['personalInfo'] = personal_data
        except:
            resp = error_resp(PROFILE_NOT_FOUND, 'PROFILE_NOT_FOUND')
            return Response(resp, CODE404)
        
        #contact info
        contact_data = {}
        mobile_list = []
        email_list = []
        
        email_list.append({'id':0, 'email':request.user.email})
        emails = UserEmail.objects.filter(user_id=request.user.id)
        for email in emails:
            email_list.append({'id':email.id, 'email':email.email, 
            'primary': False})
        
        mobiles = UserMobile.objects.filter(user_id=request.user.id)
        for mobile in mobiles:
            mobile_list.append({'id':mobile.id, 'mobile':str(mobile.mobile), 
            'code':mobile.code, 'primary': False})
        
        contact_data['emails'] = email_list
        contact_data['mobiles'] = mobile_list
        resp_data['contactInfo'] = contact_data
        
        #guardian info
        guardian_data = {}
        
        try:
            father_info = FatherInfo.objects.get(user_id=request.user.id)
            serializer = FatherInfoSerializer(father_info)
            guardian_data.update(serializer.data)
            
            mother_info = MotherInfo.objects.get(user_id=request.user.id)
            serializer = MotherInfoSerializer(mother_info)
            guardian_data.update(serializer.data)
            
            spouse_info = SpouseInfo.objects.get(user_id=request.user.id)
            serializer = SpouseInfoSerializer(spouse_info)
            guardian_data.update(serializer.data)
            
            resp_data['gurdianInfo'] = guardian_data
        except:
            resp_data['gurdianInfo'] = guardian_data
        
        #address_data
        empty_data = {'address': "", 'completeteness': 0}
        addresses = Address.objects.filter(user_id=request.user.id)
        for address in addresses:
            temp = {}
            address_data = {}

            address_serializer = AddressRetrieveSerializer(address)
            if address_serializer.data['isPermanentAddress'] == False:
                present_address = (format_str(address_serializer.data['roadNo']) +
                format_str(address_serializer.data['village']) +
                format_str(address_serializer.data['postOffice']) +
                format_str(address_serializer.data['thana']) +
                format_str(address_serializer.data['district']) +
                format_str(address_serializer.data['country']))
                
                temp.update(address_serializer.data)
                del temp['isPermanentAddress']
                del temp['sameAsPresentAddress']
                address_data['address'] = present_address[:-2]
                address_data['completeteness'] = calculate_completeness(temp.items())
                resp_data['presentAddress'] = address_data
                
            elif address_serializer.data['isPermanentAddress'] == True:
                permanent_address = (format_str(address_serializer.data['roadNo']) +
                format_str(address_serializer.data['village']) +
                format_str(address_serializer.data['postOffice']) +
                format_str(address_serializer.data['thana']) +
                format_str(address_serializer.data['district']) +
                format_str(address_serializer.data['country']))

                temp.update(address_serializer.data)
                del temp['isPermanentAddress']
                del temp['sameAsPresentAddress']
                address_data['address'] = permanent_address[:-2]
                address_data['completeteness'] = calculate_completeness(temp.items())
                resp_data['permanentAddress'] = address_data
        
        if 'permanentAddress' not in resp_data:
            resp_data['permanentAddress'] = empty_data
        if 'presentAddress' not in resp_data:
            resp_data['presentAddress'] = empty_data

        #education_data
        eduInfo = {}
        schools = []
        
        try:
            schoolInfo = SchoolInfo.objects.filter(user_id=request.user.id)
            serializer = SchoolInfoSerializerForLandingProfile(schoolInfo, many=True)
            schools.append(serializer.data)
            eduInfo['schools'] = schools
        except SchoolInfo.DoesNotExist:
            pass


        colleges = []
        try:
            collegeInfo = CollegeInfo.objects.filter(user_id=request.user.id)
            serializer = CollegeInfoSerializerForLandingProfile(collegeInfo, many=True)
            colleges.append(serializer.data)
            eduInfo['colleges'] = colleges
        except CollegeInfo.DoesNotExist:
            pass

        universities = []
        try:
            universityInfo = UniversityInfo.objects.filter(user=request.user)
            serializer = UniversityInfoSerializerForLandingProfile(universityInfo, many=True)
            universities.append(serializer.data)
            eduInfo['universities'] = universities
        except UniversityInfo.DoesNotExist:
            pass
        resp_data['eduInfo'] = eduInfo
        
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class CountriesView(ListAPIView):
    serializer_class = CountriesSerializer
    queryset = Countries.objects.all()
    permission_classes = (IsAdminOrReadOnly, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)


class DivisionsView(ListAPIView):
    serializer_class = DivisionsSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        return Division.objects.filter(country_id=self.kwargs['country_id'])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)


class DistrictsView(ListAPIView):
    serializer_class = DistrictsSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        return Districts.objects.filter(division_id=self.kwargs['division_id'])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)


class ThanaView(ListAPIView):
    serializer_class = ThanaSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        return Thana.objects.filter(district_id=self.kwargs['district_id'])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)
    

class PostOfficeView(ListAPIView):
    serializer_class = PostOfficeSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        return PostOffice.objects.filter(thana_id=self.kwargs['thana_id'])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)


class VillageView(ListAPIView):
    serializer_class = VillagesSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        return Village.objects.filter(thana_id=self.kwargs['thana_id'])
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        
        resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
        return Response(resp, CODE200)


class MobileCreateView(CreateAPIView):
    serializer_class = UserMobileSerializer
    permission_classes = (IsAdminOrAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {'user_id': request.user.id}
        serializer = UserMobileSerializer(data=request.data, context=context)
        
        if serializer.is_valid():
            ret = serializer.create()
            if ret == -3:
                resp = error_resp(INVALID_MOBILE_NUM, 'INVALID_MOBILE_NUM')
                return Response(resp, CODE400)
            resp = success_resp(MOBILE_NUM_ADD_SUCCESS, NULL, serializer.validated_data)
            return Response(resp, status=CODE201)

        resp = error_check(serializer.errors)
        return Response(resp, status=CODE400)


class MobileUpdateView(UpdateAPIView):
    serializer_class = UserMobileSerializer
    permission_classes = (IsAdminOrAuthenticated,)

    def update(self, request, *args, **kwargs):
        context = {'id': kwargs.get('id'), 'user_id': request.user.id}
        serializer = UserMobileSerializer(data=request.data, context=context)

        #user_mobile = UserMobile.objects.filter(
        #    mobile=serializer.initial_data['mobile']).exclude(id=kwargs.get('id')).exists()
        #
        #if user_mobile:
        #    resp = error_resp(MOBILE_NUM_EXISTS, 'MOBILE_NUM_EXISTS')
        #    return Response(resp, CODE400)
        
        if serializer.is_valid():
            ret = serializer.update()
            if ret == -1:
                resp = error_resp(NOT_FOUND, 'NOT_FOUND')
                return Response(resp, status=CODE404)
            
            if ret == -2:
                resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
                return Response(resp, CODE403)
            
            if ret == -3:
                resp = error_resp(INVALID_MOBILE_NUM, 'INVALID_MOBILE_NUM')
                return Response(resp, CODE400)
            
            resp = success_resp(MOBILE_NUM_UPDATE_SUCCESS, NULL, serializer.validated_data)
            return Response(resp, status=CODE200)    

        resp = error_check(serializer.errors)
        return Response(resp, status=CODE400)


class MobileDeleteView(DestroyAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    queryset = UserMobile.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            resp = error_resp(NOT_FOUND, 'NOT_FOUND')
            return Response(resp, CODE404)
        
        if instance.user.id != request.user.id:
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
        
        #if instance.primary == True:
        #    resp = error_resp(DELETE_ERROR, 'DELETE_ERROR')
        #    return Response(resp, CODE400)
        
        self.perform_destroy(instance)
        resp = error_resp(RESOURCE_DEL_SUCCESS, 'RESOURCE_DEL_SUCCESS')
        return Response(resp, CODE200)


class EmailCreateView(CreateAPIView):
    serializer_class = UserEmailSerializer
    permission_classes = (IsAdminOrAuthenticated,)

    def post(self, request, *args, **kwargs):
        context = {'user_id': request.user.id}
        serializer = UserEmailSerializer(data=request.data, context=context)

        user_email = UserEmail.objects.filter(email=serializer.initial_data['email']).exists()
        reg_email = User.objects.filter(email=serializer.initial_data['email']).exists()
        
        if reg_email or user_email:
            resp = error_resp(EMAIL_IN_USE, 'EMAIL_IN_USE')
            return Response(resp, CODE400)

        if serializer.is_valid():
            serializer.create()
            resp = success_resp(EMAIL_ADD_SUCCESS, NULL, serializer.validated_data)
            return Response(resp, status=CODE201)

        resp = error_resp(INVALID_EMAIL, 'INVALID_EMAIL')
        return Response(resp, status=CODE400)


class EmailUpdateView(UpdateAPIView):
    serializer_class = UserEmailSerializer
    permission_classes = (IsAdminOrAuthenticated,)

    def update(self, request, *args, **kwargs):
        context = {'id': kwargs.get('id'), 'user_id': request.user.id}
        serializer = UserEmailSerializer(data=request.data, context=context)

        user_email = UserEmail.objects.filter(
            email=serializer.initial_data['email']).exclude(id=kwargs.get('id')).exists()
        reg_email = User.objects.filter(email=serializer.initial_data['email']).exists()
        
        if reg_email or user_email:
            resp = error_resp(EMAIL_IN_USE, 'EMAIL_IN_USE')
            return Response(resp, CODE400)
        
        if serializer.is_valid():
            ret = serializer.update()
            
            if ret == -1:
                resp = error_resp(NOT_FOUND, 'NOT_FOUND')
                return Response(resp, status=CODE404)
            
            if ret == -2:
                resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
                return Response(resp, CODE403)
            
            resp = success_resp(EMAIL_UPDATE_SUCCESS, NULL, serializer.validated_data)
            return Response(resp, status=CODE200)    

        resp = error_resp(INVALID_EMAIL, 'INVALID_EMAIL')
        return Response(resp, status=CODE400)


class EmailDeleteView(DestroyAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    queryset = UserEmail.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            resp = error_resp(NOT_FOUND, 'NOT_FOUND')
            return Response(resp, CODE404)
        
        if instance.user.id != request.user.id:
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
        
        #if instance.primary == True:
        #    resp = error_resp(DELETE_ERROR, 'DELETE_ERROR')
        #    return Response(resp, CODE400)
        
        self.perform_destroy(instance)
        resp = error_resp(RESOURCE_DEL_SUCCESS, 'RESOURCE_DEL_SUCCESS')
        return Response(resp, CODE200)


class ContactInfo(APIView):
    permission_classes = (IsAdminOrAuthenticated,)
    
    def get(self, request):
        resp_data = {}
        mobile_list = []
        email_list = []

        email_list.append({'id':0, 'email':request.user.email})

        emails = UserEmail.objects.filter(user_id=request.user.id)
        for email in emails:
            email_list.append({'id':email.id, 'email':email.email, 
            'primary': False})
        
        mobiles = UserMobile.objects.filter(user_id=request.user.id)
        for mobile in mobiles:
            mobile_list.append({'id':mobile.id, 'mobile':str(mobile.mobile), 
            'code':mobile.code, 'primary': False})
        
        resp_data['emails'] = email_list
        resp_data['mobiles'] = mobile_list

        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class GuardianInfoCreateView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)

    def post(self, request, *args, **kwargs):
        resp_data = {}
        context = {'user_id': request.user.id}
        
        serializer = FatherInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'fatherJob')
        resolve_FK(Nationality, serializer, 'fatherNationality')
        if serializer.is_valid():
            serializer.create()
        else:
            resp = error_resp(INVALID_FATHER_INFO, 'INVALID_FATHER_INFO')
            return Response(resp, CODE400)

        serializer = MotherInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'motherJob')
        resolve_FK(Nationality, serializer, 'motherNationality')
        if serializer.is_valid():
            serializer.create()
        else:
            resp = error_resp(INVALID_MOTHER_INFO, 'INVALID_MOTHER_INFO')
            return Response(resp, CODE400)
        
        serializer = SpouseInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'spouseJob')
        resolve_FK(Nationality, serializer, 'spouseNationality')
        if serializer.is_valid():
            serializer.create()
            resp = success_resp(GUARDIAN_INFO_ADD_SUCCESS, NULL, resp_data)
            return Response(resp, CODE201)
        else:
            resp = error_resp(INVALID_SPOUSE_INFO, 'INVALID_SPOUSE_INFO')
            return Response(resp, CODE400)


class GuardianInfoUpdateView(UpdateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)

    def update(self, request, *args, **kwargs):
        resp_data = {}
        context = {'user_id': request.user.id}
        
        serializer = FatherInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'fatherJob')
        resolve_FK(Nationality, serializer, 'fatherNationality')
        if serializer.is_valid():
            serializer.update()
        else:
            resp = error_resp(INVALID_FATHER_INFO, 'INVALID_FATHER_INFO')
            return Response(resp, CODE400)

        serializer = MotherInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'motherJob')
        resolve_FK(Nationality, serializer, 'motherNationality')
        if serializer.is_valid():
            serializer.update()
        else:
            resp = error_resp(INVALID_MOTHER_INFO, 'INVALID_MOTHER_INFO')
            return Response(resp, CODE400)
        
        serializer = SpouseInfoAddSerializer(data=request.data, context=context)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        resolve_FK(Profession, serializer, 'spouseJob')
        resolve_FK(Nationality, serializer, 'spouseNationality')
        if serializer.is_valid():
            serializer.update()
            resp = success_resp(GUARDIAN_INFO_UPDATE_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)        
        else:
            resp = error_resp(INVALID_SPOUSE_INFO, 'INVALID_SPOUSE_INFO')
            return Response(resp, CODE400)


class GuardianInfoView(APIView):
    permission_classes = (IsAdminOrAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        resp_data = {}

        try:
            father_info = FatherInfo.objects.get(user_id=request.user.id)
            serializer = FatherInfoSerializer(father_info)
            resp_data.update(serializer.data)
            
            mother_info = MotherInfo.objects.get(user_id=request.user.id)
            serializer = MotherInfoSerializer(mother_info)
            resp_data.update(serializer.data)
            
            spouse_info = SpouseInfo.objects.get(user_id=request.user.id)
            serializer = SpouseInfoSerializer(spouse_info)
            resp_data.update(serializer.data)
            
            resp_data['completeness'] = calculate_completeness(resp_data.items())
            
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)
        except:
            resp = error_resp(DATA_NOT_FOUND, 'DATA_NOT_FOUND')
            return Response(resp, CODE404)

# -------------------School Info-----------------
class SchoolListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolListSerializer

    def get_queryset(self):   
        key = self.kwargs['key']
        if key == 'bd':
            try:
                country = Countries.objects.get(countryCode='880')
                return School.objects.filter(country=country)
            except:
               return []
        elif key == 'usa':
            try:
                country = Countries.objects.get(countryCode='1')
                return School.objects.filter(country=country)
            except:
               return []
        
        
    def get(self, request, *args, **kwargs):
        resp_data = []
        for school in self.list(request, *args, **kwargs).data:
            resp_data.append(school['name'])
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)#headers=RESP_HEADERS


class SchoolDetailView(RetrieveAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    queryset = School.objects.all()
    serializer_class = SchoolDetailSerializer
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        resp_data = self.retrieve(request, *args, **kwargs).data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class SchoolInfoListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolInfoRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return SchoolInfo.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        resp_data = self.list(request, *args, **kwargs).data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class SchoolInfoView(RetrieveAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolInfoRetrieveSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = SchoolInfo.objects.get(id=kwargs.get('id'), user=self.request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            return Response({'error': -1})        

    def get(self, request, *args, **kwargs):
        resp_data = self.retrieve(request, *args, **kwargs).data
        if resp_data.get('error') == -1:
            resp = error_resp(NOT_FOUND, 'NOT_FOUND')
            return Response(resp, CODE404)
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class SchoolInfoCreateView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolInfoSerializer

    def create(self, request, *args):
        serializer = self.get_serializer(data=request.data)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        
        resolve_FK(School, serializer, 'schoolName')
        resolve_choices(CLASSRANGE, serializer, 'className')
        resolve_choices(BOARD, serializer, 'boardName')
        resolve_choices(GROUP, serializer, 'field')

        serializer.initial_data.update({'user':request.user.id})
        if serializer.is_valid():
            instance = serializer.save()
            resp_data = SchoolInfoRetrieveSerializer(instance).data
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)
        
        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class SchoolInfoUpdateView(UpdateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolInfoSerializer
    queryset = SchoolInfo.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.context['this_id'] = kwargs.get('id')
        
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True

        if 'schoolName' in serializer.initial_data:
            resolve_FK(School, serializer, 'schoolName')
        if 'className' in serializer.initial_data:
            resolve_choices(CLASSRANGE, serializer, 'className')
        if 'boardName' in serializer.initial_data:
            resolve_choices(BOARD, serializer, 'boardName')
        if 'field' in serializer.initial_data:
            resolve_choices(GROUP, serializer, 'field')
        
        serializer.initial_data.update({'user':request.user.id})
        if serializer.is_valid():
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            
            resp_data = SchoolInfoRetrieveSerializer(instance).data
            resp = success_resp(UPDATE_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)
        
        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class SchoolInfoDeleteView(DestroyAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = SchoolInfoSerializer
    queryset = SchoolInfo.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
        self.perform_destroy(instance)
        resp = success_resp(DELETE_SUCCESS, NULL, {})
        return Response(resp, CODE200)

# ---------------- College Info -------------------
class CollegeListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeListSerializer

    def get_queryset(self):   
        key = self.kwargs['key']
        if key == 'bd':
            try:
                country = Countries.objects.get(countryCode='880')
                return College.objects.filter(country=country)
            except:
               return []
        elif key == 'usa':
            try:
                country = Countries.objects.get(countryCode='1')
                return College.objects.filter(country=country)
            except:
               return []
    
    def get(self, request, *args, **kwargs):
        colleges = []
        groups = []
        resp_data = {}
        
        for college in self.list(request, *args, **kwargs).data:
            groups_per_college = {}
            groupList = []
            
            colleges.append(college['name'])
            if college['scienceDept']:
                groupList.append('science')
            if college['commerceDept']:
                groupList.append('commerce')
            if college['artsDept']:
                groupList.append('arts')
            
            groups_per_college['collegeName'] = college['name']
            groups_per_college['groupList'] = groupList
            groups.append(groups_per_college)
        
        resp_data['colleges'] = colleges
        resp_data['groups'] = groups
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class CollegeDetailView(RetrieveAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    queryset = College.objects.all()
    serializer_class = CollegeDetailSerializer
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        resp_data = self.retrieve(request, *args, **kwargs).data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class CollegeInfoListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeInfoRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return CollegeInfo.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        resp_data = self.list(request, *args, **kwargs).data
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class CollegeInfoView(RetrieveAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeInfoRetrieveSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = CollegeInfo.objects.get(id=kwargs.get('id'), user=self.request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            return Response({'error': -1})
    
    def get(self, request, *args, **kwargs):
        resp_data = self.retrieve(request, *args, **kwargs).data
        if resp_data.get('error') == -1:
            resp = error_resp(NOT_FOUND, 'NOT_FOUND')
            return Response(resp, CODE404) 
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class CollegeInfoCreateView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeInfoSerializer

    def create(self, request, *args):
        serializer = self.get_serializer(data=request.data)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True

        resolve_FK(College, serializer, 'collegeName')
        resolve_choices(COLLEGE_CLASSRANGE, serializer, 'className')
        resolve_choices(BOARD, serializer, 'boardName')
        resolve_choices(GROUP, serializer, 'field')

        serializer.initial_data.update({"user":request.user.id})
        if serializer.is_valid():
            instance = serializer.save()
            resp_data = CollegeInfoRetrieveSerializer(instance).data
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)
        
        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class CollegeInfoUpdateView(UpdateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeInfoSerializer
    queryset = CollegeInfo.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
            
        serializer = self.get_serializer(instance, data=request.data)
        serializer.context['this_id'] = kwargs.get('id')

        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        
        if 'collegeName' in serializer.initial_data:
            resolve_FK(College, serializer, 'collegeName')
        if 'className' in serializer.initial_data:
            resolve_choices(COLLEGE_CLASSRANGE, serializer, 'className')
        if 'boardName' in serializer.initial_data:
            resolve_choices(BOARD, serializer, 'boardName')
        if 'field' in serializer.initial_data:
            resolve_choices(GROUP, serializer, 'field')
        
        serializer.initial_data.update({'user':request.user.id})
        if serializer.is_valid():
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            resp_data = CollegeInfoRetrieveSerializer(instance).data
            resp = success_resp(UPDATE_SUCCESS, NULL, resp_data)
            return Response(resp, CODE200)

        resp = error_check(serializer.errors)
        return Response(resp, CODE400)


class CollegeInfoDeleteView(DestroyAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = CollegeInfoSerializer
    queryset = CollegeInfo.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
        self.perform_destroy(instance)
        resp = success_resp(DELETE_SUCCESS, NULL, {})
        return Response(resp, CODE200)

# ---------------- University Info -------------------
class UniversityListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityDepartmentSerializer

    def get_queryset(self):   
        key = self.kwargs['key']
        if key == 'bd':
            try:
                country = Countries.objects.get(countryCode='880')
                return University.objects.filter(country=country)
            except:
               return []
        elif key == 'usa':
            try:
                country = Countries.objects.get(countryCode='1')
                return University.objects.filter(country=country)
            except:
               return []
    
    def get(self, request, *args, **kwargs):
        resp_data = {}
        universities = []

        queryset = self.list(request, *args, **kwargs).data
        for university in queryset:
            departmentList = []
            
            universities.append(university['name'])
            university['universityName'] = university.pop('name')
            university['departmentList'] = university.pop('department_set')
            for department in university['departmentList']:
                departmentList.append(department['name'])
            
            del university['departmentList']
            university['departmentList'] = departmentList
        
        resp_data['universities'] = universities
        resp_data['departments'] = queryset
        resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
        return Response(resp, CODE200)


class UniversityInfoListView(ListAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityInfoRetrieveSerializer

    def get_queryset(self):
        user = self.request.user
        return UniversityInfo.objects.filter(user = user)

    def get(self, request, *args, **kwargs):
        datas = self.list(request, *args, **kwargs).data
        for data in datas:
            data['university'] = data['university']['name']
            data['department'] = data['department']['name']
        resp = success_resp(FETCH_SUCCESS, NULL, datas)
        return Response(resp, CODE200)


class UniversityInfoView(RetrieveAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityInfoRetrieveSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return UniversityInfo.objects.filter(user = user)

    def get(self, request, *args, **kwargs):
        datas = self.retrieve(request, *args, **kwargs).data
        datas['university'] = datas['university']['name']
        datas['department'] = datas['department']['name']
        resp = success_resp(FETCH_SUCCESS, NULL, datas)
        return Response(resp, CODE200)


def resolve_uni_dept_FK(model, serializer, id):
    if "university" in serializer.initial_data:
        if serializer.initial_data["university"] is not None and serializer.initial_data["university"] != '':
            universityId = resolve_FK2(University, serializer.initial_data["university"])
            serializer.initial_data.update({"university":universityId})
    else :
        universityId = UniversityInfo.objects.get(id = id).university_id
            
    if "department" in serializer.initial_data:
        if serializer.initial_data["department"] is not None and serializer.initial_data["department"] != '':
            try:
                instance = model.objects.get(name__iexact=serializer.initial_data["department"], university_id = universityId)
            except:
                instance = model.objects.create(name=serializer.initial_data["department"], university_id = universityId)

            serializer.initial_data.update({"department":instance.id})


class UniversityInfoCreateView(CreateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityInfoSerializer

    def create(self, request, *args):
        serializer = self.get_serializer(data =request.data)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        data ={}
        resolve_uni_dept_FK(Department, serializer, -1)
        data.update(serializer.initial_data)
        serializer.initial_data.update({"user":request.user.id})

        if not serializer.is_valid():
            #resp = error_check(serializer.errors)
            resp = error_resp(INVALID_EDUCATION_INFO, 'INVALID_EDUCATION_INFO')
            return Response(resp, CODE404)
        serializer.save()
        resp = success_resp(FETCH_SUCCESS, NULL, data)
        return Response(resp, CODE200)


class UniversityInfoUpdateView(UpdateAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityInfoSerializer
    queryset = UniversityInfo.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
            
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if isinstance(serializer.initial_data, http.request.QueryDict):
            serializer.initial_data._mutable = True
        data ={}
        resolve_uni_dept_FK(Department, serializer, instance.id)
        data.update(serializer.initial_data)

        if not serializer.is_valid(raise_exception=True):
            resp = error_resp(INVALID_EDUCATION_INFO, 'INVALID_EDUCATION_INFO')
            return Response(resp, CODE404)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        resp = success_resp(UPDATE_SUCCESS, NULL, data)
        return Response(resp, CODE200)


class UniversityInfoDeleteView(DestroyAPIView):
    permission_classes = (IsAdminOrAuthenticated,)
    serializer_class = UniversityInfoSerializer
    queryset = UniversityInfo.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id != request.user.id:           
            resp = error_resp(UNAUTHORIZED_ACCESS, 'UNAUTHORIZED_ACCESS')
            return Response(resp, CODE403)
        self.perform_destroy(instance)
        resp = success_resp(DELETE_SUCCESS, NULL, NULL)
        return Response(resp, CODE200)

'''
class ProfileDeleteView(DestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class CountriesCreateUpdateView(CustomCreateUpdateView):
    serializer_class=CountriesSerializer
    myClass=Countries

class CountriesDeleteView(DestroyAPIView):
    serializer_class = CountriesSerializer
    queryset = Countries.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class CitiesCreateUpdateView(CustomCreateUpdateView):
    serializer_class=CitiesSerializer
    myClass=Cities

class CitiesRetrieveView(ListAPIView):
    serializer_class = CitiesSerializer
    queryset = Cities.objects.all()

class CitiesDeleteView(DestroyAPIView):
    serializer_class = CitiesSerializer
    queryset = Cities.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )
'''



'''Previous Team
class ConfigurationCreateUpdateView(CustomCreateUpdateView):
    serializer_class=ConfigurationSerializer
    myClass=Configuration

class ConfigurationRetrieveView(RetrieveAPIView):
    serializer_class = ConfigurationSerializer
    queryset = Configuration.objects.all()
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

class ConfigurationDeleteView(DestroyAPIView):
    serializer_class = ConfigurationSerializer
    queryset = Configuration.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class ContactCreateUpdateView(CustomCreateUpdateView):
    serializer_class=ContactSerializer
    myClass=Contact

class ContactRetrieveView(RetrieveAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

class ContactDeleteView(DestroyAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class FeedbackCreateUpdateView(CustomCreateUpdateView):
    serializer_class=FeedbackSerializer
    myClass=Feedback

class FeedbackRetrieveView(RetrieveAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

class FeedbackDeleteView(DestroyAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class CurrenciesCreateUpdateView(CustomCreateUpdateView):
    serializer_class=CurrenciesSerializer
    myClass=Currencies

class CurrenciesRetrieveView(RetrieveAPIView):
    serializer_class = CurrenciesSerializer
    queryset = Currencies.objects.all()
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

class CurrenciesDeleteView(DestroyAPIView):
    serializer_class = CurrenciesSerializer
    queryset = Currencies.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )

class SocialCreateUpdateView(CustomCreateUpdateView):
    serializer_class=SocialSerializer
    myClass=Social

class SocialRetrieveView(RetrieveAPIView):
    serializer_class = SocialSerializer
    queryset = Social.objects.all()
    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

class SocialDeleteView(DestroyAPIView):
    serializer_class = SocialSerializer
    queryset = Social.objects.all()
    lookup_field = "id"
    permission_classes = (IsAdminOrReadOnly, )
'''
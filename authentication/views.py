import jwt
import uuid

from django.contrib import auth
from django.conf import settings
from rest_framework import status
from django.core.cache import cache
from rest_framework import exceptions
from django.shortcuts import redirect
from django.core.mail import send_mail
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.generics import GenericAPIView, UpdateAPIView

from .models import *
from .serializers import *
from userInfo.models import Profile
from .backends import JWTAuthentication
from customized_response.response import *
from customized_response.constants import *

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.renderers import JSONRenderer
    

class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        try: 
            payload = jwt.decode(data['refresh_token'], settings.JWT_SECRET_KEY)
            try:
                user = User.objects.get(id=payload['user_id'])
            except:
                resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                raise exceptions.NotFound(resp)
            
            unique_id = uuid.uuid1().hex
            access_token = jwt.encode(
                {'jti': unique_id, 'user_id': user.id, 'username': user.username,
                'exp': datetime.utcnow() + timedelta(hours=ACS_TKN_DUR),
                'token_type': 'access'}, settings.JWT_SECRET_KEY)
            cache.set(str(user.id) + "-" + unique_id + "-acs", access_token.decode('utf-8'),
            timeout=timedelta(hours=ACS_TKN_DUR).total_seconds())
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-acs")

            refresh_token = jwt.encode(
                {'jti': unique_id, 'user_id': user.id, 'username': user.username,
                 'exp': datetime.utcnow() + timedelta(days=REF_TKN_DUR),
                 'token_type': 'refresh'}, settings.JWT_SECRET_KEY)
            cache.set(str(user.id) + "-" + unique_id + "-ref", refresh_token.decode('utf-8'),
            timeout=timedelta(days=REF_TKN_DUR).total_seconds()) 
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-ref")

        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.InvalidTokenError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except Exception as e:
            resp = error_check(data)        
            return super(CustomRenderer, self).render(resp, accepted_media_type, renderer_context)
        try:
            image_url = data['image']
        except:
            image_url = ''
        try:
            profile = Profile.objects.get(user_id=user.id)
        except:
            profile = Profile(user=user, image = image_url )
            profile.save()
        
        resp_data = {}
        resp_data.update(UserSerializer(user).data)
        resp_data['authToken'] = access_token
        resp_data['refreshToken'] = refresh_token
        
        image = str(profile.image)
        if image != '':
            # resp_data.update({'image' : settings.MEDIA_URL + image})
            resp_data.update({'image' : image})
        else:
            resp_data.update({'image' : NULL})
        
        resp = success_resp(LOG_IN_SUCCESS, NULL, resp_data) 
        res =  super(CustomRenderer, self).render(resp, accepted_media_type, renderer_context)
        return res


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True

        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)


@async_to_sync
async def mailSender(subject, message, recipient_list):
    send_mail(subject=subject, message=message,
              recipient_list=recipient_list, from_email=settings.EMAIL_HOST_USER, fail_silently=True)


class RegistrationView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=serializer.data['email'])
            token = jwt.encode(
                {'user_id': user.id, 'username': serializer.data['username'], 'exp': datetime.utcnow()+timedelta(hours=ACS_TKN_DUR)}, settings.JWT_SECRET_KEY).decode('utf-8')
 
            #async_to_sync(mailSender(WELCOME_MSG, ACC_ACTIVATE_LINK + token, [serializer.data['email']]), force_new_loop=True)
            
            send_mail(subject=WELCOME_MSG, message=ACC_ACTIVATE_LINK + token,
              recipient_list=[serializer.data['email']], from_email=settings.EMAIL_HOST_USER, fail_silently=True)
            
            resp = success_resp(USR_CREATE_SUCCESS, NULL, serializer.data)
            return Response(resp, status=CODE201)

        resp = error_check(serializer.errors)        
        return Response(resp, status=CODE400)


class ActivateView(APIView):
    def get(self, request, format=None):
        token = request.GET.get('token', '')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY)
            id = payload['user_id']
            try:
                user = User.objects.get(id=id)
            except:
                resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                raise exceptions.NotFound(resp)
            
            user.is_active = True
            user.save()
            resp = success_resp(ACC_ACTIVATE_SUCCESS, NULL, {})
            return Response(resp, CODE200)
        
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if user:      
            unique_id = uuid.uuid1().hex
            payload = {
                'jti': unique_id,
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(hours=ACS_TKN_DUR),
                'token_type': 'access'
            }
            auth_token = jwt.encode(payload, settings.JWT_SECRET_KEY) #.decode('utf-8')
            cache.set(str(user.id) + "-" + unique_id + "-acs", auth_token.decode('utf-8'),
            timeout=timedelta(hours=ACS_TKN_DUR).total_seconds())
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-acs")

            refresh_token = jwt.encode(
                {'jti': unique_id, 'user_id': user.id, 'username': user.username,
                 'exp': datetime.utcnow() + timedelta(days=REF_TKN_DUR),
                 'token_type': 'refresh'}, settings.JWT_SECRET_KEY)
            cache.set(str(user.id) + "-" + unique_id + "-ref", refresh_token.decode('utf-8'), 
            timeout=timedelta(days=REF_TKN_DUR).total_seconds())
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-ref")

            resp_data = {}
            resp_data.update(UserSerializer(user).data)
            resp_data.update({'authToken': auth_token, 'refreshToken': refresh_token})
            
            try:
                profile = Profile.objects.get(user=user.id)
                image = str(profile.image)
            except:
                image = ''
            
            if image != '':
                resp_data.update({'image' : BACKEND_DEV_BASE_URL + settings.MEDIA_URL + image})
            else:
                resp_data.update({'image' : NULL})

            resp = success_resp(LOG_IN_SUCCESS, NULL, resp_data) 
            response = Response(resp, status=CODE200)
            return response
        
        resp = error_resp(USR_PASS_INCORRECT, 'USR_PASS_INCORRECT')
        return Response(resp, status=CODE401)


class UserInfo(APIView):
    def get(self, request, format=None):
        auth_data = authentication.get_authorization_header(request)

        if not auth_data:
            resp = error_resp(EMPTY_TKN, 'EMPTY_TKN')
            return Response(resp, status=CODE400)
        prefix, token = auth_data.decode('utf-8').split(' ')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY)
            try: 
                user = User.objects.get(id=payload['user_id'])
            except:
                resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                raise exceptions.NotFound(resp)                  
           
            serializer = UserSerializer(user)
            resp = success_resp(USR_FOUND, NULL, serializer.data)
            return Response(resp, status=CODE200)
        
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        auth_data = authentication.get_authorization_header(request)
        if not auth_data:
            resp = error_resp(EMPTY_TKN, 'EMPTY_TKN')
            return Response(resp, status=CODE400)

        prefix, token = auth_data.decode('utf-8').split(' ')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY)
            try: 
                user = User.objects.get(id=payload['user_id'])
            except:
                resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                raise exceptions.NotFound(resp)                  
           
            if not user.check_password(request.data.get('old_password')):
                    resp = error_resp(WRONG_PASS, 'WRONG_PASS')
                    return Response(resp, status=CODE400)
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user.set_password(request.data.get('new_password'))
                user.save()
                resp = success_resp(PASS_CHANGE_SUCCSS, NULL, {})
                return Response(resp, status=CODE200)
            resp = error_check(serializer.errors)
            return Response(resp, status=CODE400)
            
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)


class RefreshView(APIView):
    def get(self, request, format=None):
        ref_data = request.headers.get('refresh', '')
        
        if not ref_data:
            resp = error_resp(EMPTY_TKN, 'EMPTY_TKN')
            return Response(resp, status=CODE400)

        try:
            payload = jwt.decode(ref_data, settings.JWT_SECRET_KEY)
            
            auth_cached_token = cache.get(str(payload['user_id']) + "-" + str(payload['jti']) + "-acs")
            ref_cached_token = cache.get(str(payload['user_id']) + "-" + str(payload['jti']) + "-ref")

            if not auth_cached_token or not ref_cached_token or ref_data != ref_cached_token:
                resp = error_resp(INVALID_TKN, 'INVALID_TKN')
                return Response(resp, status=CODE400)
            
            try:
                user = User.objects.get(id=payload['user_id'])
                unique_id = uuid.uuid1().hex
                auth_token = jwt.encode(
                    {
                    'jti': unique_id,
                    'user_id': user.id, 
                    'username': user.username,
                    'exp': datetime.utcnow() + timedelta(hours=ACS_TKN_DUR),
                    'token_type': 'access'}, settings.JWT_SECRET_KEY)
                
                TokenKeys.objects.get(key=str(user.id) + "-" + str(payload['jti']) + "-acs").delete()
                cache.delete(str(user.id) + "-" + str(payload['jti']) + "-acs")
                cache.set(str(user.id) + "-" + unique_id + "-acs", auth_token.decode('utf-8'),
                timeout=timedelta(hours=ACS_TKN_DUR).total_seconds())
                TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-acs")

                refresh_token = jwt.encode(
                    {'jti': unique_id, 'user_id': user.id, 'username': user.username,
                    'exp': datetime.utcnow() + timedelta(days=REF_TKN_DUR),
                    'token_type': 'refresh'}, settings.JWT_SECRET_KEY)
                TokenKeys.objects.get(key=str(user.id) + "-" + str(payload['jti']) + "-ref").delete()
                cache.delete(str(user.id) + "-" + str(payload['jti'])+ "-ref")
                cache.set(str(user.id) + "-" + unique_id + "-ref", refresh_token.decode('utf-8'),
                timeout=timedelta(days=REF_TKN_DUR).total_seconds())
                TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-ref")

                resp_data = {}
                resp_data.update(UserSerializer(user).data)
                resp_data.update({'authToken': auth_token, 'refreshToken': refresh_token})
                
                try:
                    profile = Profile.objects.get(user=user.id)
                    image = str(profile.image)
                except:
                    image = ''
            
                if image != '':
                    resp_data.update({'image' : settings.MEDIA_URL + image})
                else:
                    resp_data.update({'image' : NULL})

                resp = success_resp(ACS_TKN_GET, NULL, resp_data)
                response = Response(resp, status=CODE200)
                return response
            
            except:
                resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                raise exceptions.NotFound(resp)

        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            return Response(resp, CODE401)

       
class LogoutView(APIView):
    def get(self, request, format=None):
        ref_data = request.headers.get('refresh', '')

        if not ref_data:
            resp = error_resp(EMPTY_TKN, 'EMPTY_TKN')
            return Response(resp, status=CODE400)
        
        try:
            payload = jwt.decode(ref_data, settings.JWT_SECRET_KEY)
            
            TokenKeys.objects.get(key=str(payload['user_id']) + "-" + str(payload['jti']) + "-acs").delete()
            cache.delete(str(payload['user_id']) + "-" + str(payload.get('jti')) + "-acs")

            TokenKeys.objects.get(key=str(payload['user_id']) + "-" + str(payload['jti']) + "-ref").delete()
            cache.delete(str(payload['user_id']) + "-" + str(payload.get('jti')) + "-ref")
            
            resp = success_resp(LOG_OUT, NULL, {})
            return Response(resp, status=CODE200)
        
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            return Response(resp, CODE401) 


class LogoutAllDeviceView(APIView):
    def get(self, request, format=None):
        ref_data = request.headers.get('refresh', '')

        if not ref_data:
            resp = error_resp(EMPTY_TKN, 'EMPTY_TKN')
            return Response(resp, status=CODE400)
        
        try:
            payload = jwt.decode(ref_data, settings.JWT_SECRET_KEY)
            keys = TokenKeys.objects.filter(key__startswith=str(payload['user_id']) + '-')
            for key in keys:
                cache.delete(key)
            keys.delete()
            resp = success_resp(LOG_OUT, NULL, {})
            return Response(resp, CODE200)
        
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)


class ForgetPasswordView(GenericAPIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request, format=None):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
            unique_id = uuid.uuid1().hex
            token = jwt.encode(
                {
                'jti': unique_id,
                'user_id': user.id, 
                'username': user.username,
                'email': email, 
                'exp': datetime.utcnow() + timedelta(hours=ACS_TKN_DUR)
                }, settings.JWT_SECRET_KEY).decode('utf-8')

            cache.set(email+'_pass_reset_token', token,
                timeout=timedelta(hours=ACS_TKN_DUR).total_seconds())
            
            send_mail(subject=PASS_RESET_MSG, message=PASS_RESET_LINK + token,
              recipient_list=[email], from_email=settings.EMAIL_HOST_USER, fail_silently=True)

            resp = success_resp(ACC_FOUND, NULL, {})
            return Response(resp, status=CODE200)
        
        except:
            resp = error_resp(ACC_NOT_FOUND, 'ACC_NOT_FOUND')
            raise exceptions.NotFound(resp)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = request.GET.get('verify', '')
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY)
                email = payload['email']

                cached_token = cache.get(email+'_pass_reset_token')
                if not cached_token or token != cached_token:
                    resp = error_resp(INVALID_TKN, 'INVALID_TKN')
                    return Response(resp, status=CODE400)
            
                password = request.data.get('password', '')
                try:
                    user = User.objects.get(email=email)
                except:
                    resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                    raise exceptions.NotFound(resp)

                user.set_password(password)
                user.save()
                cache.delete(email + '_pass_reset_token')
                resp = success_resp(PASS_RESET_SUCCSS, NULL, {})
                return Response(resp, status=CODE200)
            
            except jwt.DecodeError as identifier:
                resp = error_resp(INVALID_TKN, 'INVALID_TKN')
                raise exceptions.AuthenticationFailed(resp)
            except jwt.ExpiredSignatureError as identifier:
                resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
                raise exceptions.AuthenticationFailed(resp)
        
        resp = error_check(serializer.errors)
        return Response(resp, status=CODE400)


class GoogleLogin(SocialLoginView):
    authentication_classes = [] # disable authentication
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000"
    client_class = OAuth2Client
    renderer_classes = [CustomRenderer]
    serializer_class =  SocialAccountSerializer

    def get_response(self):
        resp = super().get_response()
        data = resp.data
        data['image'] = self.serializer.validated_data['image']
        return Response(data)


class FacebookLogin(SocialLoginView):
    authentication_classes = [] # disable authentication
    adapter_class = FacebookOAuth2Adapter
    renderer_classes = [CustomRenderer]
    client_class = OAuth2Client
    serializer_class =  SocialAccountSerializer

    def get_response(self):
        resp = super().get_response()
        data = resp.data
        data['image'] = self.serializer.validated_data['image']
        return Response(data)


class AdminLoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')
        
        user = auth.authenticate(username=username, password=password)
        if user and user.groups.filter(name='admin').exists():      
            unique_id = uuid.uuid1().hex
            payload = {
                'jti': unique_id,
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(hours=ACS_TKN_DUR),
                'token_type': 'access'
            }
            auth_token = jwt.encode(payload, settings.JWT_SECRET_KEY) #.decode('utf-8')
            cache.set(str(user.id) + "-" + unique_id + "-acs", auth_token.decode('utf-8'),
            timeout=timedelta(hours=ACS_TKN_DUR).total_seconds())
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-acs")

            refresh_token = jwt.encode(
                {'jti': unique_id, 'user_id': user.id, 'username': user.username,
                 'exp': datetime.utcnow() + timedelta(days=REF_TKN_DUR),
                 'token_type': 'refresh'}, settings.JWT_SECRET_KEY)
            cache.set(str(user.id) + "-" + unique_id + "-ref", refresh_token.decode('utf-8'), 
            timeout=timedelta(days=REF_TKN_DUR).total_seconds())
            TokenKeys.objects.create(key=str(user.id) + "-" + unique_id + "-ref")

            resp_data = {}
            resp_data.update(UserSerializer(user).data)
            resp_data.update({'authToken': auth_token, 'refreshToken': refresh_token})
            
            try:
                profile = Profile.objects.get(user=user.id)
                image = str(profile.image)
            except:
                image = ''
            
            if image != '':
                resp_data.update({'image' : settings.MEDIA_URL + image})
            else:
                resp_data.update({'image' : NULL})

            resp = success_resp(LOG_IN_SUCCESS, NULL, resp_data) 
            response = Response(resp, status=CODE200)
            return response
        
        resp = error_resp(USR_PASS_INCORRECT, 'USR_PASS_INCORRECT')
        return Response(resp, status=CODE401)
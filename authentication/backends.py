import jwt
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions


from .models import TokenKeys
from customized_response.response import *
from customized_response.constants import *


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)
        if not auth_data:
            return None
        
        prefix, token = auth_data.decode('utf-8').split(' ')
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY)

            cached_token = cache.get(str(payload['user_id']) + "-" + str(payload['jti']) + "-acs")
            if cached_token and token == cached_token and payload['token_type'] == 'access':
                try:
                    user = User.objects.get(id=payload['user_id'])
                except:
                    TokenKeys.objects.get(key=str(payload['user_id']) + "-" + str(payload['jti']) + "-acs").delete()
                    cache.delete(str(payload['user_id']) + "-" + str(payload['jti']) + "-acs")

                    TokenKeys.objects.get(key=str(payload['user_id']) + "-" + str(payload['jti']) + "-ref").delete()
                    cache.delete(str(payload['user_id']) + "-" + str(payload['jti']) + "-ref")

                    resp = error_resp(USR_NOT_FOUND, 'USR_NOT_FOUND')
                    raise exceptions.NotFound(resp)
                return (user, token)
            else:
                resp = error_resp(INVALID_TKN, 'INVALID_TKN')
                raise exceptions.AuthenticationFailed(resp)
        
        except jwt.DecodeError as identifier:
            resp = error_resp(INVALID_TKN, 'INVALID_TKN')
            raise exceptions.AuthenticationFailed(resp)
        except jwt.ExpiredSignatureError as identifier:
            resp = error_resp(EXPIRED_TKN, 'EXPIRED_TKN')
            raise exceptions.AuthenticationFailed(resp)

        return super().authenticate(request)

    def authenticate_header(self, request):
        return WWW_AUTH
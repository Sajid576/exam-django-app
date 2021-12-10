from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from requests.exceptions import HTTPError
from django.utils.translation import gettext_lazy as _
from userInfo.models import Profile
from customized_response.response import *
from customized_response.constants import *
from dj_rest_auth.registration.serializers import SocialLoginSerializer
try:
    from allauth.account import app_settings as allauth_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.utils import email_address_exists, get_username_max_length
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=EMAIL_MAX_LEN, min_length=EMAIL_MIN_LEN)
    password = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, write_only=True)
    confirm = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, write_only=True)
 
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'confirm']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        confirm = attrs.get('confirm', '')
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': EMAIL_IN_USE})
        elif password != confirm:
            raise serializers.ValidationError({'confirm': PASS_NOT_MATCH})
        return super().validate(attrs)

    def save(self):
        user = User(username=self.validated_data['username'], 
            email=self.validated_data['email'])

        password = self.validated_data['password']
        user.set_password(password)
        user.is_active = False
        user.save()

        profile = Profile(user=user)
        profile.save()


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=2)
    password = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, required=True, write_only=True)
    confirm = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        password = attrs.get('new_password', '')
        confirm = attrs.get('confirm', '')
        
        if len(password) < 8 or len(confirm) < 8:
            raise serializers.ValidationError({'new_password': PASS_SHORT})
        if password != confirm:
            raise serializers.ValidationError({'confirm': PASS_NOT_MATCH})
        return super().validate(attrs)


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=EMAIL_MAX_LEN, min_length=EMAIL_MIN_LEN, required=True)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, required=True, write_only=True)
    confirm = serializers.CharField(
        max_length=PASS_MAX_LEN, min_length=PASS_MIN_LEN, style={'input_type': 'password'}, write_only=True)
    
    def validate(self, attrs):
        password = attrs.get('password', '')
        confirm = attrs.get('confirm', '')
        
        if len(password) < 8 or len(confirm) < 8:
            raise serializers.ValidationError({'password': PASS_SHORT})
        if password != confirm:
            raise serializers.ValidationError({'confirm': PASS_NOT_MATCH})
        return super().validate(attrs)
    
    #    if value.isalnum():
    #        raise serializers.ValidationError('Password Must Have Atleast One Special Character')
    #    return value


class SocialAccountSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get('access_token')
        code = attrs.get('code')
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {'access_token': access_token}
            # For sign in with apple
            id_token = attrs.get('id_token')
            if id_token:
                tokens_to_parse['id_token'] = id_token

        # Case 2: We received the authorization code
        elif code:
            self.callback_url = getattr(view, 'callback_url', None)
            self.client_class = getattr(view, 'client_class', None)

            if not self.callback_url:
                raise serializers.ValidationError(
                    _("Define callback_url in view")
                )
            if not self.client_class:
                raise serializers.ValidationError(
                    _("Define client_class in view")
                )

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth
            )
            token = client.get_access_token(code)
            access_token = token['access_token']
            tokens_to_parse = {'access_token': access_token}

            # If available we add additional data to the dictionary
            for key in ["refresh_token", "id_token", adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."))

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = get_user_model().objects.filter(
                    email=login.user.email,
                ).exists()
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address.")
                    )

            login.lookup()
            login.save(request, connect=True)
       
        attrs['user'] = login.account.user
        attrs['image'] = login.account.extra_data.get("picture")
        # print(login.account.extra_data.get("picture"))
        return attrs
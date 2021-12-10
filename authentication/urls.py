from django.urls import path, include

from .views import RegistrationView, ActivateView, LoginView 
from .views import *


urlpatterns = [  
    path('register', RegistrationView.as_view()),
    path('activate', ActivateView.as_view()),
    path('login', LoginView.as_view()),
    path('login/admin', AdminLoginView.as_view()),
    path('userinfo', UserInfo.as_view()),
    path('change-password', ChangePasswordView.as_view()),
    path('refresh', RefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    path('logout/all', LogoutAllDeviceView.as_view()),
    path('forget-password', ForgetPasswordView.as_view()),
    path('reset-password', ResetPasswordView.as_view()),
    path('social-login/google/', GoogleLogin.as_view(), name='google_login'),
    path('social-login/facebook/', FacebookLogin.as_view(), name='fb_login'),
]

from django.urls import path
from .views import *

urlpatterns = [
    path('list', NotificationlistView.as_view()),
    path('device/add', FCMAddDeviceView.as_view()),
    path('<int:id>/send', SendBulkNotifications.as_view()),
]
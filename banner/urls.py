from django.urls import path
from .views import *
urlpatterns= [
    path('list',bannerListView.as_view()),
    path('add',BannerCreateView.as_view()),
    path('<int:id>/',BannerView.as_view()),
    path('response/<int:id>/',BannnerResponseView.as_view()),
]
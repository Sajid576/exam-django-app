from django.urls import path

from .views import *


urlpatterns = [
    path('list', NewsFeedView.as_view()),
    path('add', NewsFeedCreateView.as_view()),
    path('delete/<int:pk>', NewsFeedDeleteView.as_view()),
    path('addContestNews', ContestNewsCreateView.as_view()),
]

from django.urls import path

from .views import *


urlpatterns = [
    path('list', PackageListView.as_view()),
    path('myPackage', userPackageView.as_view()),
    path('recommended', userRecommendedPackageView.as_view()),
    path('pinned', userPinnedPackageView.as_view()),
    path('<int:id>', PackageDetailView.as_view()),
    path('new', PackageCreateView.as_view()),
    path('<int:id>/exams', ExamsPerPackage.as_view()),
    path('enrollUser/<int:packageId>', enrollUserView.as_view()),
    path('doPin/<int:packageId>', doPinPackageView.as_view()),
    path('doUnPin/<int:packageId>', doUnPinPackageView.as_view()),
    path('nextExam/<id>', nextExamInPackage.as_view()),
    path('nextExam/quiz/<id>', nextQuizExamInPackage.as_view()),
]

from django.urls import path

from .views import *

urlpatterns = [
	path('list', DesignContestListView.as_view()),
	path('<int:id>', DesignContestDetailView.as_view()),
	path('<int:id>/data/submit', ContestDataSubmitView.as_view()),
	path('<int:id>/data/retrieve', ContestDataRetrieveView.as_view()),
	path('<int:id>/image/remove', FileRemoveView.as_view()),
	path('performance', UserContestPerformanceView.as_view())
]

'''
path('<int:designContestId>/enroll', EnrollUserView.as_view()),
path('<int:id>/data/submit', ContestDataSubmitView.as_view()),
'''
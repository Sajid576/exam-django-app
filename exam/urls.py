from django.urls import path

from .views import *


urlpatterns = [
    #path('examTypes/new',ExamTypeCreateView.as_view()),
    #path('examTypes',ExamTypeListView.as_view()),
    #path('new', ExamCreateView.as_view()),
    #path('list', ExamsListView.as_view()),
    #path('<int:id>', ExamDetailView.as_view()),
    #path('difficulty/new', DifficultyCreateView.as_view()),
    #path('difficultylist', DifficultyListView.as_view()),
    #path('difficulty/<int:id>', DifficultyDetailView.as_view()),
    #path('questiontype/new', QuestionTypeCreateView.as_view()),
    #path('questiontypelist', QuestionTypeListView.as_view()),
    #path('questiontype/<int:id>', QuestionTypeDetailView.as_view()),
    #path('level/new', LevelCreateView.as_view()),
    #path('levellist', LevelListView.as_view()),
    #path('level/<int:id>', LevelDetailView.as_view()),
    #path('subject/new', SubjectCreateView.as_view()),
    #path('subjectlist', SubjectsListView.as_view()),
    #path('subject/<int:id>', SubjectDetailView.as_view()),
    #path('question/new', QuestionCreateView.as_view()),
    #path('questionlist', QuestionListView.as_view()),
    #path('question/<int:id>', QuestionDetailView.as_view()),
    #path('ExamQuestionList',ExamQuestionListView.as_view()),
    #path('ExamQuestionList/<int:examId>',ExamQuestionDetailView.as_view()),
    #path('resultList', ResultListView.as_view()),
    #path('user', UserExamListView.as_view()),
    #path('UserExamResult/<int:examId>', UserExamResultView.as_view()),
    path('<int:id>/questions', QuestionsPerExam.as_view()),
    path('<int:id>/questions/quiz', QuizQuestionsPerExam.as_view()),
    path('addResult', AddResultView.as_view()),
    path('shortHistory', UserExamShortHistory.as_view()),
    path('detailsHistory/<int:id>', UserExamDetailsHistory.as_view()),
    path('progress', UserProgressView.as_view()),
    path('import', BulkImportView.as_view()),
]


''' Previous Team
path('events', EventExamView.as_view()),
path('<int:examId>/questionList', QuestionsPerExam.as_view()),
path('<int:examId>/subject/<int:subjectId>/questionList', QuestionListView.as_view()),
path('<int:examId>/subject/<int:subjectId>/question/new', QuestionCreateView.as_view()),
path('<int:examId>/subject/<int:subjectId>/question/<int:id>', QuestionDetailView.as_view()),
path('<int:id>/start', StartedView.as_view()),
path('<int:id>/stop', EndedExamView.as_view()),
path('<int:id>/enroll', EnrollMentView.as_view()),
path('<int:qid>/answer/<int:option>', AnsweredView.as_view()),
path('<int:examId>/submit_answer_list', AnsweredListVew.as_view()),
path('<int:examId>/marksList', MarksListView.as_view()),
path('<int:examId>/marksPerUser', MarksPerUser.as_view()),
path('<int:examId>/mark/<int:id>', MarkDetailView.as_view()),
path('<int:examId>/mark/new', MarkCreateView.as_view()),
'''
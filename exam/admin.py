from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import *


admin.site.register(ExamType)
admin.site.register(Exam)
admin.site.register(Difficulty)
admin.site.register(QuestionType)
admin.site.register(Level)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(ExamQuestion)
admin.site.register(Result)
admin.site.register(UserExam)
admin.site.register(UserExamPerformance)


'''Previous Team
admin.site.register(EventExam)
admin.site.register(Enrollment)
admin.site.register(Started)
admin.site.register(Answered)
admin.site.register(Mark)

# @admin.register(ExamQuestion)
# class ExamQuestionAdmin(admin.ModelAdmin):
#     list_display = ("ExamId","QuestionId")

from import_export import resources

class QuestionResource(resources.ModelResource):

    class Meta:
        model = Question

class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource

admin.site.register(Question, QuestionAdmin)
'''
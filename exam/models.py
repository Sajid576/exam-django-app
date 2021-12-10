from django.db import models
from django.utils import timezone
from django.core.validators import *
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import DateRangeField

from package.models import Package


OPTION = (
    (1, 'option1'),
    (2, 'option2'),
    (3, 'option3'),
    (4, 'option4'),
)


class Difficulty(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class QuestionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Level(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
        
class Chapter(models.Model):
    chapterNumber = models.IntegerField()
    name = models.CharField(max_length=255, blank = True)
    level = models.ForeignKey(to=Level, on_delete=models.CASCADE)

class Topic(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(to=Subject, on_delete=models.CASCADE)

class Question(models.Model):
    imgFile = models.ImageField(upload_to='quesImg', blank=True, null=True)
    statement = models.TextField(blank=False)
    option1 = models.TextField(blank=False)
    option2 = models.TextField(blank=False)
    option3 = models.TextField(blank=True)
    option4 = models.TextField(blank=True)
    hint = models.TextField(blank=True)
    estimatedTime = models.DurationField(default=timedelta)
    trueFalse = models.BooleanField(default=False)
    fillBlank = models.BooleanField(default=False)
    correctAnswer = models.IntegerField(choices=OPTION, default=1)
    explanation = models.TextField(blank=True)
    markPerQues = models.FloatField(default=1.0)
    difficulty = models.ForeignKey(to=Difficulty, related_name='questions', on_delete=models.CASCADE)
    questionType = models.ForeignKey(to=QuestionType, related_name='questions', on_delete=models.CASCADE)
    level = models.ForeignKey(to=Level, related_name='questions', on_delete=models.CASCADE)
    subject = models.ForeignKey(to=Subject, related_name='questions', on_delete=models.CASCADE)
    chapter = models.ForeignKey(to=Chapter, related_name='questions', on_delete=models.CASCADE,blank=True, null=True)
    topic = models.ForeignKey(to=Topic, related_name='questions', on_delete=models.CASCADE,blank=True, null=True)
    
    def __str__(self):
        return str('%s - %s' % (self.subject, self.statement))

class ExamType(models.Model):
    name =models.CharField(max_length=30,unique=True)
    
    def __str__(self):
        return f"{self.name}"

class Exam(models.Model):
    name = models.CharField(max_length=255)
    instruction = models.TextField(blank = True)
    duration = models.DurationField(default=timedelta)
    startTime = models.DateTimeField(default=timezone.now, null = True)
    passingPercent = models.FloatField(validators=[MaxValueValidator(100)],default=40)
    negativePercentage = models.FloatField(default=0.0,validators=[MaxValueValidator(100)])
    paidExam = models.BooleanField(default=True)
    totalQuestion=models.IntegerField(default=0)
    totalMark = models.FloatField(default=100)
    isManual = models.BooleanField(default=True)
    examType = models.ForeignKey(to=ExamType,on_delete=models.CASCADE, null = True)
    questions = models.ManyToManyField(Question, through='ExamQuestion')
    package = models.ForeignKey(to=Package, related_name='exams', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class ExamQuestion(models.Model):
    examId = models.ForeignKey(to=Exam,on_delete = models.CASCADE)
    questionId = models.ForeignKey(to=Question,on_delete = models.CASCADE)
    
    class Meta:
        unique_together=['examId', 'questionId']
    
    def __str__(self):
        return  f"{self.examId},{self.questionId}"

class Result(models.Model):
    userId = models.ForeignKey(to = User,on_delete=models.CASCADE)
    examId = models.ForeignKey(to=Exam,on_delete = models.CASCADE)
    questionId = models.ForeignKey(to=Question,on_delete = models.CASCADE)
    providedAnswer = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ['examId', 'userId', 'questionId']
    
    def __str__(self):
        return f"{self.userId},{self.examId},{self.questionId},{self.providedAnswer}"

class UserExam(models.Model):
    examId = models.ForeignKey(to=Exam, on_delete=models.CASCADE)
    userId = models.ForeignKey(to=User, on_delete=models.CASCADE)
    shuffleId = models.IntegerField(default=0)
    participationCount = models.IntegerField()
    examDate = models.DateTimeField()
    consumedTime = models.DurationField(null=True)
    obtainedMarks = models.FloatField()
    totalCorrectedQuestions = models.IntegerField()
    totalIncorrectedQuestions = models.IntegerField()
    viewAble = models.BooleanField()
    retakeAble = models.BooleanField()
    
    class Meta:
        unique_together = ['examId', 'userId']
    
    def __str__(self):
        return  f"{self.userId}-{self.examId}"


class UserExamPerformance(models.Model):
    dateRange = DateRangeField()
    viewCount = models.IntegerField(default=0)
    retakeCount = models.IntegerField(default=0)
    exam = models.ForeignKey(to=Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['exam', 'user', 'dateRange']
    
    def __str__(self):
        return str('%s - %s - %s' % (self.user, self.exam, self.dateRange))


'''PREVIOUS TEAM
EXAM_TYPE = (
    ('marathon', 'MARATHON'),
    ('single', 'SINGLE'),
    ('timer', 'TIMER'),
)

EVENT_TYPE = (
    ('marathon', 'MARATHON'),
    ('single', 'SINGLE'),
    ('timer', 'TIMER'),
)


class EventExam(models.Model):
    exam = models.ForeignKey(to=Exam, on_delete=models.CASCADE)
    starts_at = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    eventType = models.CharField(max_length=50, choices=EVENT_TYPE, default='marathon')


class Enrollment(models.Model):
    class Meta:
        unique_together = [['event', 'owner']]
    event = models.ForeignKey(to=EventExam, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Started(models.Model):
    class Meta:
        unique_together = [['exam', 'owner']]
        verbose_name_plural = "Started"
    exam = models.ForeignKey(to=Exam, on_delete=models.CASCADE)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True)
    exam_finished = models.BooleanField(default=False)


class Answered(models.Model):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    answer = models.IntegerField(default=0)

    class Meta:
        unique_together = [['question', 'user']]
        verbose_name_plural = "Answered"


class Mark(models.Model):
    user = models.ForeignKey(to=User,to_field='username', on_delete=models.CASCADE)
    exam = models.ForeignKey(to=Exam, on_delete=models.CASCADE)
    subject = models.ForeignKey(to=Subject, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=0)
    untouched = models.IntegerField(default=0)
    wrong = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
    marks_lost =  models.FloatField(default=0.0)
    total =  models.FloatField(default=0.0)
    percentage =  models.FloatField(default=0.0)
    highest_marks =  models.FloatField(default=0.0)
    status =  models.CharField(max_length=255)

    def __str__(self):
        return str('%s - %s - %s - Total Marks: %s' % (self.user, self.exam, self.subject, self.total))
'''


from rest_framework import status
from django.db.models import fields
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.response import Response

from .models import *

'''
class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= ExamType
        fields= '__all__'

class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = '__all__'

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=ExamQuestion
        fields='__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model =Result
        fields= ['providedAnswer']

class UserExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExam
        fields = ['examDate', 'obtainedMarks', 'viewAble', 'retakeAble']
'''

class QuestionSerializer(serializers.ModelSerializer):
    # imgFile = serializers.SerializerMethodField()

    class Meta:
        model = Question
        exclude = ['correctAnswer']

    # def get_imgFile(self, question):
    #     request = self.context.get('request')
    #     if question.imgFile and hasattr(question, 'imgFile'):
    #         imgFile = question.imgFile.url
    #         return request.build_absolute_uri(imgFile)
    #     return None
    
    def to_representation(self, instance):
        rep = super(QuestionSerializer, self).to_representation(instance)
        rep['difficulty'] = instance.difficulty.name
        rep['questionType'] = instance.questionType.name
        rep['level'] = instance.level.name
        rep['subject'] = instance.subject.name
        return rep


class QuestionSerializerWithCorrectAnswer(QuestionSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionsPerExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'name', 'instruction', 'duration', 'startTime', 'passingPercent', 
        'negativePercentage', 'paidExam', 'totalQuestion', 'totalMark', 'isManual',
        'examType', 'questions']
        
    def to_representation(self, instance):
        rep = super(QuestionsPerExamSerializer, self).to_representation(instance)
        rep['examType'] = instance.examType.name
        return rep


class QuestionsPerExamSerializerWithCorrectAnswer(QuestionsPerExamSerializer):
    questions = QuestionSerializerWithCorrectAnswer(many=True, read_only=True)


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        exclude = ['questions', 'package']

    def to_representation(self, instance):
        rep = super(ExamSerializer, self).to_representation(instance)
        rep['examType'] = instance.examType.name
        return rep


class QuestionImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['imgFile']


class ExamImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        exclude = ['questions']


''' Previous Team
class EventExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventExam
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = []

class StartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Started
        fields = []

class StartedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Started
        fields = []

class AnsweredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answered
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

    def validate(self, data):
        question = data['question']
        if Answered.objects.filter(user=self.context["request"].user, question=question).exists():
            raise serializers.ValidationError(
                "You have already answered this question")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        obj = Answered.objects.create(**validated_data, user=user)
        obj.save()
        return obj

class CorrectAnswerField(serializers.RelatedField):
    def to_representation(self, value):
        return '%d' % (value.answer)

class AnsweredWithCorrectAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all())
    correct_answer = serializers.IntegerField(
        source='question.answer', read_only=True)

    class Meta:
        model = Answered
        fields = ['question', 'correct_answer', 'answer']

class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'

class UserExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__' 
'''
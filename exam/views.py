import json
import base64
from PIL import Image
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import status, exceptions
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, RetrieveAPIView, DestroyAPIView

from .models import *
from .serializers import *
from customized_response.response import *
from customized_response.constants import *
from package.models import Package, User_Package
from package.serializers import PackageImportSerializer
from authentication.serializers import UserSerializer


class IsAdmin(permissions.BasePermission):
    message = error_resp(PERMISSION_DENIED, 'PERMISSION_DENIED')
    
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user:
            return True
        elif not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            raise exceptions.NotAuthenticated(resp)
        else:
            return False


class IsAdminOrAuthenticated(permissions.BasePermission): 
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if super_user or user.is_authenticated:
            return True
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        raise exceptions.NotAuthenticated(resp)


class IsAdminOrEnrolled(permissions.BasePermission):
    message = error_resp(NOT_ENROLLED, 'NOT_ENROLLED')

    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser
        if not user.is_authenticated:
            resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
            raise exceptions.NotAuthenticated(resp)

        examId = view.kwargs.get('id', 0)
        exam = Exam.objects.get(id=examId)
        enrolled = User_Package.objects.filter(
            user_id=user.id, package_id=exam.package).exists()
        return super_user or enrolled


def resolve_FK(model, serializer, field):
    if serializer.initial_data[field] is not None:
        try:
            instance = model.objects.get(name__iexact=serializer.initial_data[field])
        except:
            instance = model.objects.create(name=serializer.initial_data[field])

        serializer.initial_data.update({field:instance.id})


def set_image(img_field, image):
    if image != "":
        format, img_str = image.split(';base64,')
        _name, ext = format.split('/')
        name = _name.split(':')[-1]
        img = ContentFile(base64.b64decode(img_str), name='{}.{}'.format(name, ext))
        img_field.save(name + '.' + ext, img, save=True)


class BulkImportView(APIView):
    # permission_classes = (IsAdmin,)

    def post(self, request):
        packages = request.data['packages'].copy()
        for package in packages:
            exams = package['exams'].copy()
            del package['exams']

            package_serializer = PackageImportSerializer(data=package)
            if package_serializer.is_valid():
                package_instance = Package.objects.create(**package_serializer.validated_data)
                set_image(package_instance.titleImageUrl, package['image'])
            else:
                resp = error_resp(PACK_BULK_IMPORT_FAIL, 'PACK_BULK_IMPORT_FAIL')
                return Response(resp, status=CODE400)
            
            for exam in exams:
                questions = exam['questions'].copy()
                del exam['questions']
                exam_serializer = ExamImportSerializer(data=exam)
                exam_serializer.initial_data.update({'package':package_instance.id})
                resolve_FK(ExamType, exam_serializer, 'examType')

                if exam_serializer.is_valid():
                    exam_instance = Exam.objects.create(**exam_serializer.validated_data)
                    package_instance.examCount += 1
                else:
                    resp = error_resp(EXAM_BULK_IMPORT_FAIL, 'EXAM_BULK_IMPORT_FAIL')
                    return Response(resp, status=CODE400)

                for question in questions:
                    question_serializer = QuestionImportSerializer(data=question)    
                    resolve_FK(Difficulty, question_serializer, 'difficulty')
                    resolve_FK(QuestionType, question_serializer, 'questionType')
                    resolve_FK(Level, question_serializer, 'level')
                    resolve_FK(Subject, question_serializer, 'subject')
                    resolve_FK(Chapter, question_serializer, 'chapter')
                    resolve_FK(Topic, question_serializer, 'topic')

                    if question_serializer.is_valid():
                        question_instance = Question.objects.create(**question_serializer.validated_data)
                        set_image(question_instance.imgFile, question['image'])
                        exam_instance.duration += question_instance.estimatedTime
                        exam_instance.totalQuestion += 1
                        exam_instance.totalMark += question_instance.markPerQues
                        exam_instance.questions.add(question_instance)
                    else:
                        resp = error_resp(QUES_BULK_IMPORT_FAIL, 'QUES_BULK_IMPORT_FAIL')
                        return Response(resp, status=CODE400)
                exam_instance.save()        
            package_instance.save()
        resp = success_resp(BULK_IMPORT_SUCCESS, NULL, {})
        return Response(resp, status=CODE200)


class QuestionsPerExam(RetrieveAPIView):
    serializer_class = QuestionsPerExamSerializer
    queryset = Exam.objects.all()
    lookup_field = 'id'
    permission_classes = (IsAdminOrEnrolled,)
    
    def retrieve(self, request, *args, **kwargs):
        examId = kwargs.get('id')
        try:
            exam = Exam.objects.get(id=examId)
            package = Package.objects.get(id=exam.package_id)
            userExam = UserExam.objects.get(userId_id=request.user.id, examId_id=examId)
            if package.fee == 0 or (userExam.participationCount < 2 and userExam.retakeAble == True):
                start_date = START_DATE
                end_date = start_date + timedelta(days=6)
                today = datetime.utcnow().date()
                while(True):
                    if today <= end_date and today >= start_date:
                        user_performance, created = UserExamPerformance.objects.get_or_create(
                        user=self.request.user, exam_id=examId,
                        dateRange=(start_date, end_date + timedelta(days=1)))
                        
                        user_performance.retakeCount += 1
                        user_performance.save()
                        break
                    else:
                        start_date = end_date + timedelta(days=1)
                        end_date = start_date + timedelta(days=6)
                
                userExam.participationCount += 1
                userExam.examDate = datetime.now(UTC)
                userExam.save()

                instance = self.get_object()
                serializer = self.get_serializer(instance)
                resp = success_resp(FETCH_SUCCESS, NULL, serializer.data)
                return Response(resp, status=CODE200)
            else:
                resp = error_resp(EXAM_NOT_ALLOWED, 'EXAM_NOT_ALLOWED')
                return Response(resp, status=CODE400)
        except:
            resp = error_resp(EXAM_NOT_ALLOWED, 'EXAM_NOT_ALLOWED')
            return Response(resp, status=CODE400)


class QuizQuestionsPerExam(QuestionsPerExam):
    serializer_class = QuestionsPerExamSerializerWithCorrectAnswer


class AddResultView(APIView):
    permission_classes = (IsAdminOrAuthenticated, )

    def post(self, request, *args, **kwargs):
        finishTime = datetime.now(UTC)
        data = json.loads(request.body)
        examId = data.get('examId')
        exam = Exam.objects.get(id=examId)
        package = Package.objects.get(id=exam.package_id)
        userExam = UserExam.objects.get(examId_id=examId, userId_id=request.user.id)
        
        count = userExam.participationCount
        timeTaken = finishTime - userExam.examDate
        timeTaken = timeTaken if timeTaken < exam.duration else exam.duration 
        #if timeTaken > exam.duration + timedelta(minutes=2):
        #	resp = error_resp(RESULT_ADD_ERROR, 'RESULT_ADD_ERROR')
        #   return Response(resp, status=CODE400)
        
        if package.fee == 0 or (count <= 2 and userExam.retakeAble == True):
            givenAnswer = data.get('givenAnswer')
            obtainedMarks = 0
            totalCorrectedQuestions = 0
            totalIncorrectedQuestions = 0
            for answer in givenAnswer:
                questionId = answer.get('questionId')
                optionId = answer.get('optionId')
                if optionId != "":
                    optionId = int(optionId)
                question = Question.objects.get(id=questionId)
                correctOption = question.correctAnswer
                if optionId == "":
                    pass
                elif correctOption == optionId:
                    obtainedMarks += question.markPerQues
                    totalCorrectedQuestions += 1
                else:
                    totalIncorrectedQuestions += 1
                    obtainedMarks -= (exam.negativePercentage * question.markPerQues)/100
                try:
                    prevInstance = Result.objects.get(examId_id=examId, 
                    questionId_id=questionId, userId_id=request.user.id)
                except Result.DoesNotExist:
                    prevInstance = None
                if prevInstance is not None:
                    prevInstance.delete()
                result = Result(examId_id=examId, questionId_id=questionId, 
                userId_id=request.user.id, providedAnswer=optionId)
                result.save()

            totalMark = exam.totalMark
            passingPercentage = exam.passingPercent
            percentage = (obtainedMarks * 100)/totalMark
            viewAble = True
            retakeAble = False
            
            if percentage > VIEW_HISTORY_THRESHOLD:
                viewAble = False
            if percentage < passingPercentage and count == 1:
                retakeAble = True
            if package.fee == 0:
                viewAble = True
                retakeAble = True
            
            userExam.consumedTime = timeTaken 
            userExam.obtainedMarks = obtainedMarks
            userExam.totalCorrectedQuestions=totalCorrectedQuestions
            userExam.totalIncorrectedQuestions=totalIncorrectedQuestions
            userExam.viewAble=viewAble
            userExam.retakeAble=retakeAble
            userExam.save()

            resp = success_resp(RESULT_ADDED, NULL, {})
            return Response(resp, status=CODE200)
        else:
            resp = error_resp(RESULT_ADD_ERROR, 'RESULT_ADD_ERROR')
            return Response(resp, status=CODE400)


class UserExamShortHistory(APIView):
    permission_classes = (IsAdminOrAuthenticated, )

    def get(self, request, *args, **kwargs):
        result_data = {}
        weeks = []
        week_no = 1
        total_participated_exam = 0
        total_marks = 0
        total_obtained_marks = 0
        total_questions = 0
        total_corrected_questions = 0

        start_date = START_DATE
        end_date = start_date + timedelta(days=6)
        today = datetime.utcnow().date()

        while start_date <= today:
            exams = UserExam.objects.filter(userId_id=request.user.id, 
            examDate__date__gte=start_date, examDate__date__lte=end_date)
               
            user_performance = UserExamPerformance.objects.filter(user=request.user, 
            dateRange=(start_date, end_date + timedelta(days=1)))

            weekly_result = {}
            results_array = []
            total_participated_exam_per_week = 0
            total_corrected_questions_per_week = 0
            total_questions_per_week = 0
            total_obtained_marks_per_week = 0
            total_marks_per_week = 0
            view_count_per_week = 0
            retake_count_per_week = 0

            for exam in exams:
                this_exam = Exam.objects.get(pk=exam.examId_id)
                
                total_participated_exam_per_week += 1 
                total_corrected_questions_per_week += exam.totalCorrectedQuestions
                total_questions_per_week += this_exam.totalQuestion
                total_obtained_marks_per_week += exam.obtainedMarks
                total_marks_per_week += this_exam.totalMark 
                
                try:
                    packageName = Package.objects.get(id=this_exam.package.id).name
                except:
                    packageName = ""
                result = {
                    "packageName": packageName,
                    "examId": exam.examId_id,
                    "name": this_exam.name,
                    "duration": str(this_exam.duration),
                    "examDate": exam.examDate.date(),
                    "totalQuestions": this_exam.totalQuestion,
                    "totalMarks": this_exam.totalMark,
                    "negativeMark":this_exam.negativePercentage,
                    "totalCorrectedQuestions": exam.totalCorrectedQuestions,
                    "totalIncorrectedQuestions":exam.totalIncorrectedQuestions,
                    "obtainedMarks": exam.obtainedMarks,
                    "viewAble": exam.viewAble,
                    "retakeAble": exam.retakeAble,
                    "consumedTime": str(exam.consumedTime)
                }
                results_array.append(result)
                    
            if len(results_array) == 0:
                start_date = end_date + timedelta(days=1)
                end_date = start_date + timedelta(days=6)
                continue
            
            try:
                weekly_accuray = (total_corrected_questions_per_week / total_questions_per_week)*100
            except:
                weekly_accuray = 0
            try:
                weekly_marks_accuray = (total_obtained_marks_per_week / total_marks_per_week)*100
            except:
                weekly_marks_accuray = 0
            
            for instance in user_performance:
                view_count_per_week += instance.viewCount
                retake_count_per_week += instance.retakeCount
            
            weekly_result['dateRange'] = str(start_date) + ' to ' + str(end_date)
            weekly_result['totalParticipatedExamPerWeek'] = total_participated_exam_per_week
            weekly_result['viewCountPerWeek'] = view_count_per_week
            weekly_result['retakeCountPerWeek'] = retake_count_per_week
            weekly_result['weeklyAccuracy'] = weekly_accuray
            weekly_result['points'] = weekly_marks_accuray
            weekly_result['results'] = results_array
            weeks.append(weekly_result)
            
            total_participated_exam += total_participated_exam_per_week
            total_obtained_marks += total_obtained_marks_per_week
            total_corrected_questions += total_corrected_questions_per_week
            total_questions += total_questions_per_week
            total_marks += total_marks_per_week
            week_no += 1
            
            start_date = end_date + timedelta(days=1)
            end_date = start_date + timedelta(days=6)
        
        try:
            lifetime_accuracy = (total_corrected_questions / total_questions)*100
        except:
            lifetime_accuracy = 0
        
        try:
            lifetime_marks_accuracy = (total_obtained_marks / total_marks)*100
        except:
            lifetime_marks_accuracy = 0
        
        curr_week_start_date = start_date - timedelta(days=7)
        prev_week_start_date = start_date - timedelta(days=14)

        for week in weeks:
            tmp_date = datetime.strptime(week['dateRange'].split()[0], "%Y-%m-%d").date()
            if tmp_date == prev_week_start_date:
                week['previousWeek'] = True
            else:
                week['previousWeek'] = False 
            
            if tmp_date == curr_week_start_date:
                week['currentWeek'] = True
            else:
                week['currentWeek'] = False 
            
            week['weeklyAccuracy'] -= lifetime_accuracy
            week['points']  -= lifetime_marks_accuracy
        
        result_data['totalParticipatedExam'] = total_participated_exam 
        result_data['totalPoint'] = total_obtained_marks
        result_data['lifetimeAccuracy'] = lifetime_accuracy
        result_data['lifetimeMarksAccuracy'] = lifetime_marks_accuracy
        result_data['weeks'] = weeks[::-1]
        
        resp = success_resp(FETCH_SUCCESS, NULL, result_data)
        return Response(resp, status=CODE200)


class UserExamDetailsHistory(APIView):
    permission_classes = (IsAdminOrAuthenticated,)

    def get(self, request, *args, **kwargs):
        result_data = {}
        results_array = []
        examId = kwargs.get('id')
        
        try:
            this_exam = Exam.objects.get(pk=examId)
            userExam = UserExam.objects.get(userId_id=request.user.id, examId_id=examId)
        except:
            resp = error_resp(EXAM_NOT_FOUND, 'EXAM_NOT_FOUND')
            return Response(resp, status=CODE404)
        
        if userExam.viewAble is False:
            resp = error_resp(VIEW_HISTORY_THRESHOLD_EXCEEDED, 'VIEW_HISTORY_THRESHOLD_EXCEEDED')
            return Response(resp, status=CODE401)
        
        start_date = START_DATE
        end_date = start_date + timedelta(days=6)
        today = datetime.utcnow().date()
        while(True):
            if today <= end_date and today >= start_date:
                user_performance, created = UserExamPerformance.objects.get_or_create(
                    user=self.request.user,
                    exam_id=examId, dateRange=(start_date, end_date + timedelta(days=1)))

                user_performance.viewCount += 1
                user_performance.save()
                break
            else:
                start_date = end_date + timedelta(days=1)
                end_date = start_date + timedelta(days=6)

        result_data.update(ExamSerializer(this_exam).data)
        result_data['examDate'] = userExam.examDate.astimezone(BD_TIME).date()
        result_data['obtainedMarks'] = userExam.obtainedMarks
        result_data['totalCorrectedQuestions'] = userExam.totalCorrectedQuestions
        result_data['totalIncorrectedQuestions'] = userExam.totalIncorrectedQuestions
        result_data['retakeAble'] = userExam.retakeAble
        result_data['consumedTime'] = str(userExam.consumedTime)
        resultsPerQuestions = Result.objects.filter(examId_id=examId, 
        	userId_id=request.user.id)
        for questionResults in resultsPerQuestions:
            this_question = Question.objects.get(pk=questionResults.questionId_id)
            correct_answer = str(this_question.correctAnswer)
            result = {}
            result.update(QuestionSerializer(this_question).data)
            result['correctAnswer'] = correct_answer
            result['givenAnswer'] = questionResults.providedAnswer
            results_array.append(result)
        result_data['results'] = results_array
        resp = success_resp(FETCH_SUCCESS, NULL, result_data)
        return Response(resp, status=CODE200)


class UserProgressView(APIView):
    def get(self, request,*args,**kwargs):
        if request.user.is_authenticated:
            userId= User.objects.get(pk=request.user.id)
            enddate = date.today()
            progress_data = {}
            progress_array = []
            i = 1
            while i <= 12:
                startdate = enddate.replace(day=1)
                exams=UserExam.objects.filter(userId=userId, examDate__date__gte=startdate, examDate__date__lte=enddate).values()
                total_exams = len(exams)
                obtained_marks = 0
                total_marks = 0
                for exam in exams:
                    obtained_marks += exam['obtainedMarks']
                    this_exam = Exam.objects.get(pk=exam['examId_id'])
                    total_marks += this_exam.totalMark
                progress = {
                    'year' : startdate.year,
                    'month' : startdate.month,
                    'total_exams': total_exams,
                    'total_marks': total_marks,
                    'obtained_marks': obtained_marks,
                }
                progress_array.append(progress)
                enddate =  startdate - timedelta(days=1)
                i += 1
            progress_data['progress'] = progress_array
            
            resp = success_resp(FETCH_SUCCESS, NULL, progress_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)
'''
json format for result

{
    "examId": 1,
    "examDate": "2021-01-11",
    "givenAnswer": [{
        "questionId": 1,
        "optionId": "1"
    },
    {
        "questionId": 2,
        "optionId": "2" 
    }]
}
'''

'''
class DifficultyCreateView(CreateAPIView):
    serializer_class = DifficultySerializer
    queryset = Difficulty.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class DifficultyListView(ListAPIView):
    serializer_class = DifficultySerializer
    queryset = Difficulty.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class DifficultyDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DifficultySerializer
    queryset = Difficulty.objects.all()
    lookup_field = 'id'
    #permission_classes = (permissions.IsAdminUser, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = success_resp('Fetch Successful', 'NULL', serializer.data)
        return Response(resp)

class QuestionTypeCreateView(CreateAPIView):
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class QuestionTypeListView(ListAPIView):
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class QuestionTypeDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()
    lookup_field = 'id'
    permission_classes = (permissions.IsAdminUser, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = success_resp('Fetch Successful', 'NULL', serializer.data)
        return Response(resp)

class LevelCreateView(CreateAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class LevelListView(ListAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class LevelDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()
    lookup_field = 'id'
    permission_classes = (permissions.IsAdminUser, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = success_resp('Fetch Successful', 'NULL', serializer.data)
        return Response(resp)

class SubjectCreateView(CreateAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class SubjectsListView(ListAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    permission_classes = (permissions.IsAdminUser, )

class SubjectDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    lookup_field = 'id'
    permission_classes = (permissions.IsAdminUser, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = success_resp('Fetch Successful', 'NULL', serializer.data)
        return Response(resp)

class QuestionCreateView(CreateAPIView):
    serializer_class = QuestionCreateSerializer
    parser_classes = (JSONParser, FormParser, MultiPartParser)
    permission_classes = (IsAdminOrAuthenticated, )
    
    def post(self,request,*args,**kwargs):
        serializer = QuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            examId = serializer.data.get("exam")
            questionId = serializer.data.get("id")
            exam = Exam.objects.get(pk=examId)
            ques = Question.objects.get(pk=questionId)
            exam.duration += ques.estimatedTime
            exam.totalQuestion += 1
            exam.totalMark += ques.markPerQues
            exam.save() 
            obj = ExamQuestion(examId = exam,questionId = ques)
            obj.save()
        else:
            return Response("serializer not valid")
        return Response(serializer.data,status= status.HTTP_201_CREATED)

class QuestionListView(ListAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = (IsAdminOrAuthenticated, )

class QuestionDetailView(RetrieveAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    lookup_field = 'id'
    #permission_classes = (permissions.IsAdminUser, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = success_resp('Fetch Successful', 'NULL', serializer.data)
        return Response(resp)

class ExamTypeCreateView(CreateAPIView):
    serializer_class = ExamTypeSerializer
    permission_classes = (permissions.IsAdminUser,)
    
class ExamTypeListView(ListAPIView):
    serializer_class = ExamTypeSerializer
    queryset = ExamType.objects.all()
    #permission_classes=(IsAdminOrAuthenticated,)

class ExamCreateView(CreateAPIView):
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()
    permission_classes=(IsAdminOrAuthenticated,)

class ExamsListView(ListAPIView):
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()
    permission_classes=(IsAdminOrAuthenticated,)

class ExamDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()
    lookup_field = 'id'
    #permission_classes = (IsAdminOrAuthenticated,)

class ExamQuestionListView(ListAPIView):
    serializer_class = ExamQuestionSerializer
    queryset = ExamQuestion.objects.all()
    #permission_classes=(IsAdminOrAuthenticated,)

class ExamQuestionDetailView(ListAPIView):
    serializer_class=ExamQuestionSerializer
    queryset= ExamQuestion.objects.all()
    lookup_field = 'examId'
    #permission_classes=(IsAdminOrAuthenticated,)

class ResultListView(ListAPIView):
    serializer_class=ResultSerializer
    queryset=Result.objects.all()
    permission_classes=(IsAdminOrAuthenticated,)

class UserExamListView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated :
            resp_data = {}
            exams = []
            user = User.objects.get(pk=request.user.id)
            queryset = UserExam.objects.filter(userId=user.id)
            resp_data.update(UserSerializer(user).data)
            
            for elem in queryset:
                exam = Exam.objects.get(pk=elem.examId_id)
                userExam = {}
                exam_serializer = ExamSerializer(exam)          
                userExam.update(exam_serializer.data)
                userExam.update(UserExamSerializer(elem).data)
                exams.append(userExam)
            
            resp_data.update({'exams':exams})
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)

class UserExamResultView(APIView):
    serializer_class=ResultSerializer
    permission_classes=(IsAdminOrAuthenticated,)

    def get(self, request,*args,**kwargs):
        if request.user.is_authenticated :
            resp_data = {}
            questions = []
            examId = kwargs.get('examId',' ')
            userId = request.user.id
            user = User.objects.get(pk=userId)
            queryset = Result.objects.filter(examId=examId, userId=userId).values()  
            resp_data.update(UserSerializer(user).data)
            
            instance = UserExam.objects.filter(userId=user.id, examId=examId).values()
            if len(instance) > 0: 
                exam = Exam.objects.get(pk=examId)
                exam_serializer = ExamSerializer(exam)         
                new_exam_serializer = dict(exam_serializer.data)
                new_exam_serializer.update(UserExamSerializer(instance[0]).data)
                resp_data.update({'exam':new_exam_serializer})
            else: 
                resp_data.update({'exam':{}})
            
            for elem in queryset:
                question = Question.objects.get(pk=elem['questionId_id'])
                question_serializer = QuestionSerializerWithCorrectAnswer(question)
                new_question_serializer = dict(question_serializer.data)
                new_question_serializer.update(ResultSerializer(elem).data)
                questions.append(new_question_serializer)
            
            resp_data.update({'questions':questions})
            resp = success_resp(FETCH_SUCCESS, NULL, resp_data)
            return Response(resp, status=CODE200)
        
        resp = error_resp(AUTH_CRE_NOT_FOUND, 'AUTH_CRE_NOT_FOUND')
        return Response(resp, status=CODE401)
'''








''' PREVIOUS TEAM
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_admin = request.user and request.user.is_superuser
        return request.method in permissions.SAFE_METHODS or is_admin

class IsAdminOrEnrolled(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser

        if not user.is_authenticated:
            return False

        exam_id = view.kwargs.get('examId', 0)
        enrolled = Enrollment.objects.filter(
            exam__id=exam_id, owner=user).exists()

        return super_user or enrolled

class QuestionsPerExam(APIView):  
    permission_classes=(IsAdminOrAuthenticated,)
    def get(self, request, *args, **kwargs):
        temp=[]
        examId = kwargs.get('examId', '')
        ques= ExamQuestion.objects.filter(ExamId=examId)
        for  q in ques:
            h=Question.objects.get(pk=q.pk)
            serializer  = QuestionSerializer(h)
            temp.append(serializer.data)
        return Response(temp)

class UserExamCreateView(CreateAPIView):
    permission_classes=(IsAdminOrAuthenticated,)
    serializer_class = UserExamSerializer
    queryset = UserExam.objects.all()

class EventExamView(ListAPIView):
    serializer_class = EventExamSerializer
    queryset = EventExam.objects.all()

class EnrollMentView(GenericAPIView):
    
    def post(self, request, id=None):
        # check if user present in the request
        user = request.user
        if not user.is_authenticated:
            return Response("You are not logged in", status=status.HTTP_401_UNAUTHORIZED)

        if not id:
            return Response("Invalid request", status=status.HTTP_400_BAD_REQUEST)

        # check if exam id exists by looing into Enrollment table
        try:
            event = EventExam.objects.get(pk=id)
        except ObjectDoesNotExist as identifier:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)

        obj = Enrollment(owner=user, event=event)

        try:
            obj.save()
        except IntegrityError as identifier:
            return Response("You are already enrolled for this exam", status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

class StartedView(GenericAPIView):
    permission_classes = (IsAdminOrEnrolled,)

    def post(self, request, id=None):
        # check if user present in the request
        user = request.user

        # check if exam id exists by looing into Started table
        try:
            exam = Exam.objects.get(pk=id)
        except ObjectDoesNotExist as identifier:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)

        obj = Started(exam=exam, owner=user)

        try:
            obj.save()
        except:
            return Response("You already started this exam", status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

class AnsweredView(GenericAPIView):
    # permission_classes = (IsAdminOrEnrolled,)

    def post(self, request, qid=None, option=None):
        user = request.user
        # check if question id exists by looing into Answered table
        try:
            question = Question.objects.get(pk=qid)
        except ObjectDoesNotExist as identifier:
            return Response("Not found", status=status.HTTP_404_NOT_FOUND)

        obj = Answered(question=question, user=user, answer=option)

        try:
            obj.save()
        except IntegrityError as identifier:
            return Response("You already answered this question", status=status.HTTP_200_OK)

        serializers = AnsweredWithCorrectAnswerSerializer(obj)
        return Response(data=serializers.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)

class AnsweredListVew(ListAPIView):
    # permission_classes = (IsAdminOrEnrolled,)
    serializer_class = AnsweredSerializer

    # def post(self, request, *args, **kwargs):
    #     is_many = isinstance(request.data, list)

    #     serializer = self.get_serializer(
    #         data=request.data, many=True)
    #     if serializer.is_valid():
    #         self.perform_create(serializer)
    #         headers = self.get_success_headers(serializer.data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        user = request.user
        query_set = Answered.objects.filter(user=user)
        serializer = AnsweredSerializer(query_set, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class EndedExamView(GenericAPIView):
    permission_classes = (IsAdminOrEnrolled,)

    def post(self, request, id=None):
        user = request.user

        try:
            exam = Exam.objects.get(pk=id)
            obj = Started.objects.get(owner=user, exam=exam)
            obj.ended_at = datetime.now()
            obj.exam_finished = True
            obj.save()
        except:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

        serializer = StartedSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarksListView(ListAPIView):
    serializer_class = MarkSerializer
    
    def get_queryset(self):
        examId = self.kwargs['examId']
        return Mark.objects.filter(exam=examId)
    # permission_classes = (IsAdminOrEnrolled, )

class MarksPerUser(ListAPIView):
    serializer_class = MarkSerializer
    
    def get_queryset(self):
        user = self.request.user
        examId = self.kwargs['examId']
        return Mark.objects.filter(user=user, exam=examId) 

class MarkCreateView(GenericAPIView):
    serializer_class = MarkSerializer
    
    def post(self, request, **kwargs):
        user = request.user
        mydictionary={}
        mydictionary['user']=user
        for field in request.data:
                if(field=='exam'):
                    mydictionary[field]=Exam.objects.get(pk=request.data['exam'])
                    continue
                if(field=='subject'):
                    mydictionary[field]=Subject.objects.get(pk=request.data['subject'])
                    continue
                mydictionary[field]=request.data[field]    
        else:
            if('user' in request.data):
                if(User.objects.filter(id=request.data['user']).exists()):
                    mydictionary['user']=User.objects.get(id=request.data['user'])
                else:
                    return Response("User does not exist", status=status.HTTP_400_BAD_REQUEST)
        
        obj = Mark(**mydictionary)

        for field in obj.__dict__:
            if(field=='id' or field=='user_id'):
                continue

        try:
            obj.save()
        except IntegrityError as identifier:
            print(identifier)
            return Response("Data already Exists", status=status.HTTP_200_OK)

        return Response("Created", status=status.HTTP_200_OK)

class MarkDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = MarkSerializer

    def get_queryset(self):
        examId = self.kwargs['examId']
        return Mark.objects.filter(exam=examId)
    lookup_field = "id"
    # permission_classes = (IsAdminOrEnrolled, )

    #     class AddResultView(APIView):
    # def post(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         data = json.loads(request.body)
    #         examId = data.get('ExamId')
    #         examDate = data.get('ExamDate')
    #         obtainedMarks = data.get('ObtainedMarks')
    #         givenAnswer = data.get('GivenAnswer')
    #         for answer in givenAnswer:
    #             questionId = answer.get('QustionId')
    #             optionId = answer.get('OptionId')
    #             # if Result.objects.get(ExamId_id = examId, QuestionId_id=questionId, UserId_id = request.user.id).DoesNotExist :
    #             #     print ("not exist till")
    #             try:
    #                 prevInstance = Result.objects.get(ExamId_id = examId, QuestionId_id=questionId, UserId_id = request.user.id)
    #                 if prevInstance is not None:
    #                     prevInstance.delete()
    #             except  ObjectDoesNotExist:
    #                 result = Result(ExamId_id=examId, QuestionId_id=questionId, UserId_id=request.user.id, ProvidedAnswer=optionId)
    #                 result.save() 
    #         prevInstance= None
    #         try:
    #             prevInstance = UserExam.objects.get(ExamId_id = examId, UserId_id = request.user.id)         
    #         except ObjectDoesNotExist:
    #             pass
    #         if prevInstance is not None:
    #             print("deleted")
    #             prevInstance.delete()          
    #         userExam = UserExam(ExamId_id=examId, UserId_id=request.user.id, ExamDate=examDate, ObtainedMarks=obtainedMarks)
    #         userExam.save()
    #         return Response("result added")
    #     return Response("login required")
'''
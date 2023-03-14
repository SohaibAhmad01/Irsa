from core.views import LargeResultsSetPagination, IsAdmin
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lms_irsa.settings import EMAIL_HOST_USER
from django.utils import timezone
from django.http import JsonResponse
from .serializers import StudentSerializer
from .models import Student
from core.models import User, News
from core.serializers import UserSerializer, NewsSerializer
from programmodule.models import Programs, Course
from programmodule.serializers import ProgramSerializer, CourseSerializer
from classmodule.models import Class
from core.views import send_mail_to_user
import datetime
from threading import Thread
import logging

db_logger = logging.getLogger('db')


# Create your views here.


class StudentView(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('created_time')
    serializer_class = StudentSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LargeResultsSetPagination

    def update(self, request, *args, **kwargs):
        if 'roll_number' in request.data:
            return Response('Roll number can not change', status=status.HTTP_400_BAD_REQUEST)
        if 'email' in request.data:
            return Response('Email can not change', status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Student updated successfully, student_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Student deleted successfully, student_id:{instance.id}",
             'status': status.HTTP_200_OK})
        if instance.image:
            instance.image.storage.delete(instance.image.name)
        instance.user.delete()
        return Response({
            'success': True,
            'message': "Student deleted successfully"
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        request.data._mutable = True
        request.data['password'] = 'Pass12345'
        data = request.data
        data['role'] = 'student'
        check_user = User.objects.filter(email=data["email"]).first()
        if check_user:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"User already registered, student_email:{check_user.email}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': 'User already registered',
            }, status=status.HTTP_400_BAD_REQUEST)
        check_student = self.queryset.filter(roll_number=data['roll_number']).first()
        if check_student:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"Student with this roll number already exist, student_email:{check_student.user.email}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': 'Student with this roll number already exist',
            }, status=status.HTTP_400_BAD_REQUEST)
        user = UserSerializer(data=data)
        if user.is_valid():
            user = user.save()
            user.set_password(data["password"])
            user.save()
            data['user'] = user.id
            serializer = StudentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                ctx = {
                    'link': 'https://irsa.edu.pk/forget-password'
                }
                subject = 'Welcome to IRSA'
                thread = Thread(target=send_mail_to_user,
                                args=(subject, 'admin_welcome_email.html', ctx, EMAIL_HOST_USER, [data["email"]]))
                thread.start()
                response = serializer.data
                response['message'] = 'Account created successfully'
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': f"Student registered successfully, student_email:{data['email']}",
                     'status': status.HTTP_201_CREATED})
                return Response(serializer.data)
            else:
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': f"{serializer.errors}, student_email:{data['email']}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'success': False,
                    'message': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"{user.errors}, student_email:{data['email']}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': user.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_student_profile(self, request, pk):
        user = request.user
        get_object = self.queryset.filter(id=pk).first()
        if get_object:
            response = UserSerializer(get_object.user).data
            return JsonResponse(response)
        else:
            return Response({
                'success': False,
                'message': 'Student does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    def update_student_program(self, request, pk):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        instance = self.queryset.filter(id=pk).first()
        if instance:
            check_program = Programs.objects.filter(id=request.data['programs']).first()
            if check_program:
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': f"Update student program successfully, student_id:{instance.id},"
                                f" student_previous_program_id: {instance.program}, updated_program_id: {check_program.id}",
                     'status': status.HTTP_200_OK})
                instance.program = check_program
                instance.save()
                return Response({
                    'success': True,
                    'message': 'Successfully program added in student'
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Program not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'message': 'student does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_own_profile(request):
        user = request.user
        if user.role == 'student':
            serializer = UserSerializer(user).data
            return JsonResponse(serializer)
        else:
            return Response({
                'success': False,
                'message': 'User does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_student_stats(request):
        if request.user.role == 'student':
            all_programs = Programs.objects.all()
            program_response = ProgramSerializer(all_programs, many=True).data
            all_courses = Course.objects.all()
            course_response = CourseSerializer(all_courses, many=True).data
            news_objects = News.objects.all()
            news_response = NewsSerializer(news_objects, many=True).data
            classes_count = Class.objects.filter(student_list=request.user.studentuser)
            return Response({'programs': program_response, 'courses': course_response, 'events': news_response,
                             'class_count': len(classes_count)})
        else:
            return Response('Only student stats show here', status=status.HTTP_400_BAD_REQUEST)

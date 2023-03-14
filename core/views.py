from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.template.loader import render_to_string
from rest_framework.permissions import BasePermission
from random import randint
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from lms_irsa.settings import EMAIL_HOST_USER
from django.utils import timezone
import datetime
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from rest_framework.views import APIView
import requests
from .models import User, OtpTemp, News
from .serializers import AdminUserSerializer, UserSerializer, NewsSerializer
from teachermodule.serializers import TeacherAllDataSerializer, StudentAllDataSerializer
from studentmodule.models import Student
from teachermodule.models import Teacher
from programmodule.models import Course
from rest_framework import filters
from threading import Thread
import datetime
import logging

db_logger = logging.getLogger('db')


def send_mail_to_user(subject, template_name, context, from_email, to_email):
    subject = subject
    html_content = render_to_string(template_name=template_name, context=context)
    text_content = render_to_string(template_name=template_name, context=context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = 'related'
    msg.send()


class IsAdmin(BasePermission):
    """
       Allows access only to admins
    """

    def has_permission(self, request, view):
        if 'irsa_classes/getclass' in request.build_absolute_uri():
            if request.user.role == 'teacher' or request.user.role == 'student' or request.user.role == 'admin':
                return True
        if 'student_auth/me' in request.build_absolute_uri():
            if request.user.role == 'student':
                return True
        if 'teacher_auth/me' in request.build_absolute_uri():
            if request.user.role == 'teacher':
                return True
        if 'teacher/stats' in request.build_absolute_uri():
            if request.user.role == 'teacher':
                return True
        if 'student/stats' in request.build_absolute_uri():
            if request.user.role == 'student':
                return True
        if 'program' in request.build_absolute_uri() or 'course' in request.build_absolute_uri():
            if request.method == 'GET':
                if request.user.role == 'teacher' or request.user.role == 'student':
                    return True
        if request.user.role == 'admin':
            return True
        return False


class IsAdminOrTeacher(BasePermission):
    """
       Allows access only to admins
    """

    def has_permission(self, request, view):
        if 'attendance/edit' in request.build_absolute_uri():
            if request.user.role == 'admin':
                return True
        if 'course_content/getbycourseid' in request.build_absolute_uri():
            if request.user.role == 'student':
                return True
        if request.user.role == 'admin' or request.user.role == 'teacher':
            return True
        return False


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ForgotResetPasswordView(viewsets.ModelViewSet):

    @staticmethod
    def reset_password_by_student(request, pk):
        get_user = OtpTemp.objects.filter(otp=pk).first()
        if get_user:
            if len(request.data['password']) < 8:
                return Response({
                    'error': True,
                    'message': 'Password length should be greater than 8'
                }, status=status.HTTP_400_BAD_REQUEST)
            instance = get_user.user
            instance.set_password(request.data['password'])
            instance.is_active = True
            instance.save()
            return Response({
                'success': True,
                'message': 'You password changed successfully.'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': True,
                'message': 'User does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def forgot_password(request):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        email = request.data.get('email')
        if email:
            check_email = User.objects.filter(email=email).first()
            if check_email:
                otp_value = randint(100000, 999999)
                ctx = {
                    'otp': otp_value
                }
                subject = 'Forgot password'
                thread = Thread(target=send_mail_to_user,
                                args=(subject, 'forgot_password.html', ctx, EMAIL_HOST_USER, [check_email.email]))
                thread.start()
                otp, created = OtpTemp.objects.get_or_create(user=check_email)
                otp.generated_time = datetime.datetime.now() + timedelta(hours=2)
                otp.otp = otp_value
                otp.save()
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': email, 'Date': now_date,
                     'Time': now_time,
                     'message': f"Otp ({otp_value}) send to {email}",
                     'status': status.HTTP_200_OK})
                return Response({
                    'success': True,
                    'message': 'Otp send to email.'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'User does not exist'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Email not found'
            }, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def reset_password(request):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        otp_value = request.data.get('otp')
        password = request.data.get('password')
        if len(password) < 8:
            return Response({
                'success': False,
                'message': 'Length of password should greater than 8'
            }, status=status.HTTP_400_BAD_REQUEST)
        if otp_value:
            if password:
                check_otp = OtpTemp.objects.filter(otp=otp_value).first()
                if check_otp:
                    if check_otp.generated_time > timezone.now():
                        check_otp.user.set_password(password)
                        check_otp.user.is_active = True
                        check_otp.user.save()
                        db_logger.info(
                            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': check_otp.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"Otp ({otp_value}), Password successfully reset for {check_otp.user.email}",
                             'status': status.HTTP_200_OK})
                        return Response({
                            'success': True,
                            'message': 'password changed.'
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            'success': False,
                            'message': 'OTP expired'
                        }, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    'success': False,
                    'message': 'user does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'success': False,
                    'message': 'Entered password'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Otp not found, please enter Otp'
            }, status=status.HTTP_400_BAD_REQUEST)


def get_jwt_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'accessToken': str(refresh.access_token)
    }


class Login(viewsets.ModelViewSet):

    def create(self, request, *args, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        user = User.objects.filter(email=request.data["email"]).first()
        if user:
            if user.check_password(request.data["password"]):
                tokens = get_jwt_token(user)
                if user.is_staff and user.is_active:
                    user_data = UserSerializer(user).data
                    user_data['isSuperAdmin'] = True
                elif user.role == 'admin' and user.is_active:
                    user_data = AdminUserSerializer(user.adminuser).data
                    user_data['isSuperAdmin'] = False
                elif user.role == 'student' and user.is_active:
                    user_data = StudentAllDataSerializer(user.studentuser).data
                    user_data['isSuperAdmin'] = False
                elif user.role == 'teacher' and user.is_active:
                    user_data = TeacherAllDataSerializer(user.teacheruser).data
                    user_data['isSuperAdmin'] = False
                else:
                    return Response({
                        'error': True,
                        'message': 'User does not exist'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user_data['accessToken'] = tokens['accessToken']
                user_data['refresh'] = tokens['refresh']
                user_data['role'] = user.role
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': user.email, 'Date': now_date,
                     'Time': now_time,
                     'message': f"User login successfully, role: {user.role}",
                     'status': status.HTTP_200_OK})
                return Response(user_data, status=status.HTTP_200_OK)
            else:
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': user.email, 'Date': now_date,
                     'Time': now_time,
                     'message': f"Invalid password, email:{request.data['email']}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'error': False,
                    'message': 'Invalid credentials'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            db_logger.error(
                {'url': request.build_absolute_uri(), 'payload': request.data, 'Date': now_date, 'Time': now_time,
                 'message': f"Email not found, email:{request.data['email']}",
                 'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                "error": False,
                'code': status.HTTP_404_NOT_FOUND,
                "message": "Invalid credentials"
            }, status=status.HTTP_404_NOT_FOUND)


class RefreshView(APIView):

    @staticmethod
    def post(request):
        try:
            json_data = {'refresh': request.data['refresh']}
            response = requests.post('https://lmsirsaapp.herokuapp.com/api/token/refresh/', json=json_data)
            req_data = response.json()
            return Response({
                'accessToken': req_data['access'],
            })
        except Exception as e:
            return Response({'error': True, 'message': e})


class NewsSection(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by('created_time')
    serializer_class = NewsSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"News created, news_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
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
             'message': f"News updated successfully, news_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Record updated successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"News deleted successfully, news_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            instance.delete()
            return Response({
                'success': True,
                'message': "News deleted successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)


class StatsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdmin,)

    def list(self, request, *args, **kwargs):
        get_students = Student.objects.filter()
        get_courses = Course.objects.filter()
        get_teachers = Teacher.objects.filter()
        return Response({
            'totalCourses': len(get_courses),
            'totalStudents': len(get_students),
            'totalTeachers': len(get_teachers),
        })


class NewsList(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get('filterStatus'):
            search_status_list = request.GET.get('filterStatus').split(',')
            queryset = queryset.filter(type__in=search_status_list)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

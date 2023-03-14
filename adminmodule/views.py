from rest_framework import viewsets
from core.views import IsAdmin, IsAuthenticated, LargeResultsSetPagination
from .models import AdminUser
from .serializers import AdminUserSerializer
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from core.models import User, News
from core.views import send_mail_to_user
from lms_irsa.settings import EMAIL_HOST_USER
from programmodule.models import Programs, Course
from studentmodule.models import Student
from teachermodule.models import Teacher
from programmodule.serializers import ProgramSerializer, CourseSerializer
from core.serializers import NewsSerializer, UserSerializer
import datetime
from threading import Thread
import logging
import base64
from django.core.files.base import ContentFile

db_logger = logging.getLogger('db')


# Create your views here.
class AdminUserView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = AdminUser.objects.all().order_by('created_time')
    serializer_class = AdminUserSerializer
    pagination_class = LargeResultsSetPagination

    def update(self, request, *args, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        if 'email' in request.data:
            db_logger.error(
                {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                 'Date': now_date, 'Time': now_time,
                 'message': 'Email can not update', 'status': status.HTTP_400_BAD_REQUEST})
            return Response('Email can not change', status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if 'image' in request.data:
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            format, imgstr = request.data['image'].split(';base64,')
            ext = format.split('/')[-1]
            img = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            request.data['image'] = img
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Admin updated successfully, admin_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Admin updated successfully")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def get_own_profile(request):
        user = request.user
        serializer = UserSerializer(user).data
        return JsonResponse(serializer)

    def create(self, request, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        if request.user.is_staff:
            data = request.data
            data['role'] = 'admin'
            data['password'] = 'Pass1234'
            check_user = User.objects.filter(email=data["email"]).first()
            if check_user:
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': 'Email Already exists', 'Try to create user with email': check_user.email,
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'success': False,
                    'message': 'Email Already exists',
                }, status=status.HTTP_400_BAD_REQUEST)
            user = UserSerializer(data=data)
            if user.is_valid():
                user = user.save()
                user.set_password(data["password"])
                user.save()
                data['user'] = user.id
                format, imgstr = data['image'].split(';base64,')
                ext = format.split('/')[-1]
                img = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                request.data['image'] = img
                user_profile = AdminUserSerializer(data=data)
                if user_profile.is_valid():
                    user_profile.save()
                    ctx = {
                        'link': 'https://irsa.edu.pk/forget-password'
                    }
                    subject = 'Welcome to IRSA'
                    thread = Thread(target=send_mail_to_user,
                                    args=(subject, 'admin_welcome_email.html', ctx, EMAIL_HOST_USER, [data["email"]]))
                    thread.start()
                    user_profile.data['role'] = data['role']
                    now_date = datetime.datetime.now().strftime("%d-%m-%Y")
                    now_time = datetime.datetime.now().strftime("%H:%M:%S")
                    db_logger.info(
                        {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                         'Date': now_date, 'Time': now_time,
                         'message': f"Admin created successfully, admin_email:{request.data['email']}",
                         'status': status.HTTP_201_CREATED})
                    return Response("Admin registered successfully")
                else:
                    db_logger.error(
                        {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                         'Date': now_date, 'Time': now_time,
                         'message': user_profile.errors, 'admin_email': user.email,
                         'status': status.HTTP_400_BAD_REQUEST})
                    return Response({
                        'message': user_profile.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': user.errors,
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'message': user.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': 'Only super admin can add admin',
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': 'Only super admin can add admin'
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_admin_profile(self, request, pk):
        user = request.user
        if user.is_staff:
            get_object = self.queryset.filter(id=pk).first()
            if get_object:
                response = AdminUserSerializer(get_object).data
                return JsonResponse(response)
            else:
                return Response({
                    'success': False,
                    'message': 'User does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'message': 'Only super admin can see admins'
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        instance = self.get_object()
        if request.user.is_staff:
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"User deleted, deleted_user{instance.user.email}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            instance.user.delete()
            return Response("Admin deleted successfully")
        else:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"Only super admin can delete other admin, deleted_user{instance.user.email}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response('Only super admin can delete other admin', status=status.HTTP_400_BAD_REQUEST)

    def get_admin_stats(self, request):
        all_programs = Programs.objects.all()
        all_students = Student.objects.all()
        all_teachers = Teacher.objects.all()
        program_response = ProgramSerializer(all_programs, many=True).data
        all_courses = Course.objects.all()
        course_response = CourseSerializer(all_courses, many=True).data
        news_objects = News.objects.filter()
        news_response = NewsSerializer(news_objects, many=True).data
        return Response({'programs': program_response, 'courses': course_response, 'events': news_response,
                         'totalCourses': len(all_courses), 'totalStudents': len(all_students),
                         'totalTeachers': len(all_teachers)})

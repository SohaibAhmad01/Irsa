from rest_framework import viewsets, status
from .models import *
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from lms_irsa.settings import EMAIL_HOST_USER
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import generics
from rest_framework import filters
from core.views import IsAdmin, LargeResultsSetPagination
from core.serializers import UserSerializer
from core.models import News
from core.serializers import NewsSerializer
from programmodule.models import Programs, Course
from programmodule.serializers import ProgramSerializer, CourseSerializer
from classmodule.models import Class
import datetime
from core.views import send_mail_to_user
from threading import Thread
import logging

db_logger = logging.getLogger('db')


# Create your views here.
class TeacherView(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().order_by('created_time')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    filter_backends = [filters.SearchFilter]
    search_fields = ['firstname', 'lastname']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        user = request.user
        # request.data._mutable = True
        data = request.data
        data._mutable = True
        data['password'] = 'Pass12345'
        data['role'] = 'teacher'
        check_user = User.objects.filter(email=data["email"]).first()
        if check_user:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"User already registered, teacher_email:{check_user.email}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': 'User already registered',
            }, status=status.HTTP_400_BAD_REQUEST)
        user = UserSerializer(data=data)
        if user.is_valid():
            user = user.save()
            user.set_password(data["password"])
            user.save()
            data['user'] = user.id
            serializer = TeacherSerializer(data=data)
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
                     'message': f"Teacher created registered, teacher_email:{data['email']}",
                     'status': status.HTTP_201_CREATED})
                return Response(serializer.data)
            else:
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': f"{serializer.errors}, teacher_email:{data['email']}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'success': False,
                    'message': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': f"{user.errors}, teacher_email:{data['email']}",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response({
                'success': False,
                'message': user.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_own_profile(request):
        user = request.user
        if user.role == 'teacher':
            serializer = UserSerializer(user).data
            return JsonResponse(serializer)
        else:
            return Response({
                'success': False,
                'message': 'User does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    def get_teacher_profile(self, request, pk):
        user = request.user
        get_object = self.queryset.filter(id=pk).first()
        if get_object:
            response = TeacherSerializer(get_object).data
            return JsonResponse(response)
        else:
            return Response({
                'success': False,
                'message': 'Teacher does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    def update_password(self, request):
        user = request.user
        if user:
            if len(request.data['newPassword']) < 8:
                return Response({
                    'error': True,
                    'message': 'Length of password should be greater than 8'
                }, status=status.HTTP_400_BAD_REQUEST)
            password = request.data['currentPassword']
            if password:
                if user.check_password(password):
                    user.set_password(request.data['newPassword'])
                    user.save()
                    return Response({
                        'success': True,
                        'message': 'Password changed successfully'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'message': 'Current password incorrect'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'success': False,
                    'message': 'New password required.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "success": False,
                'message': 'User does not exists'
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.queryset.filter(id=kwargs['pk']).first()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Teacher deleted successfully, teacher_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            instance.user.delete()
            return Response({
                'success': True,
                'message': 'Teacher deleted successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': True,
                'message': 'teacher does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
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
             'message': f"Teacher updated successfully, teacher_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_teacher_stats(self, request):
        if request.user.role == 'teacher':
            all_programs = Programs.objects.all()
            program_response = ProgramSerializer(all_programs, many=True).data
            all_courses = Course.objects.all()
            course_response = CourseSerializer(all_courses, many=True).data
            news_objects = News.objects.filter()
            classes_count = Class.objects.filter(teacher=request.user.teacheruser)
            news_response = NewsSerializer(news_objects, many=True).data
            return Response({'programs': program_response, 'courses': course_response, 'events': news_response,
                             'class_count': len(classes_count)})
        else:
            return Response('Only teacher stats show here', status=status.HTTP_400_BAD_REQUEST)


class TeacherList(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['firstname', 'lastname']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get('filterStatus'):
            search_status_list = request.GET.get('filterStatus').split(',')
            if not len(search_status_list) > 1:
                queryset = queryset.filter(status=search_status_list[0])
        if request.GET.get('filterPrograms'):
            if queryset:
                search_program_list = request.GET.get('filterPrograms').split(',')
                get_course = Course.objects.filter(program_id__in=search_program_list)
                get_class = Class.objects.filter(course__in=get_course)
                teachers_ids = get_class.values_list('teacher_id', flat=True)
                queryset = Teacher.objects.filter(id__in=teachers_ids)
            else:
                queryset = Teacher.objects.none()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

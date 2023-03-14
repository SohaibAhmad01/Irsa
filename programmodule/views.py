from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Programs, Course, CourseContent
from .serializers import ProgramSerializer, CourseSerializer, CourseContentSerializer
from core.views import LargeResultsSetPagination, IsAdmin, IsAuthenticated, IsAdminOrTeacher
from rest_framework.response import Response
from rest_framework import generics, filters
import datetime
import logging

db_logger = logging.getLogger('db')


# Create your views here.
class ProgramView(viewsets.ModelViewSet):
    queryset = Programs.objects.all().order_by('created_time')
    serializer_class = ProgramSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        if request.GET.get('searchText'):
            queryset = self.queryset.filter(title__icontains=request.GET.get('searchText'))
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Program created successfully, program_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("Program Created successfully")

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
             'message': f"Program updated successfully, program_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response({
            'message': 'Program updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Program deleted successfully, program_id:{instance.id}",
             'status': status.HTTP_200_OK})
        if instance.image:
            instance.image.storage.delete(instance.image.name)
        instance.delete()
        return Response({
            'success': True,
            'message': "program deleted successfully"
        }, status=status.HTTP_200_OK)


class CourseView(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('created_time')
    serializer_class = CourseSerializer
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
             'message': f"Course created successfully, course_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        if request.GET.get('searchText'):
            queryset = self.queryset.filter(title__icontains=request.GET.get('searchText'))
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
             'message': f"Course updated successfully, course_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Course deleted successfully, course_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            instance.delete()
            return Response({
                'success': True,
                'message': "Course deleted successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'course not found'
            }, status=status.HTTP_404_NOT_FOUND)


class CourseContentView(viewsets.ModelViewSet):
    queryset = CourseContent.objects.all().order_by('created_time')
    serializer_class = CourseContentSerializer
    permission_classes = (IsAuthenticated, IsAdminOrTeacher)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Course content created successfully, course_content_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("courseContent Created successfully")

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
             'message': f"Course content updated successfully, course_content_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("course updated successfully")

    def get_content_by_course(self, request, pk):
        get_course = Course.objects.filter(id=pk).first()
        if get_course:
            course_data = CourseSerializer(get_course).data
            all_objects = self.queryset.filter(course=pk)
            if all_objects:
                assignment_response = {}
                document_response = {}
                video_response = {}
                assignment_obj = all_objects.filter(type='ASSIGNMENT')
                document_obj = all_objects.filter(type='DOCUMENT')
                video_obj = all_objects.filter(type='VIDEO')
                assignment_response['type'] = 'Assignment'
                document_response['type'] = 'Document'
                video_response['type'] = 'Video'
                if assignment_obj:
                    assignment_response['result'] = CourseContentSerializer(assignment_obj, many=True).data
                else:
                    assignment_response['result'] = []
                if document_obj:
                    document_response['result'] = CourseContentSerializer(document_obj, many=True).data
                else:
                    document_response['result'] = []
                if video_obj:
                    video_response['result'] = CourseContentSerializer(video_obj, many=True).data
                else:
                    video_response['result'] = []
                return Response({
                    'assignment': assignment_response,
                    'document': document_response,
                    'video': video_response, 'course': course_data})
            else:
                return Response({
                    'result': [], 'course': course_data})
        else:
            return Response('course not found')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Course content deleted successfully, course_content_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            instance.delete()
            return Response({
                'success': True,
                'message': "Content deleted successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'course content not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ProgramList(generics.ListAPIView):
    queryset = Programs.objects.all()
    serializer_class = ProgramSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

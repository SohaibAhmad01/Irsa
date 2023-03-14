from rest_framework import viewsets, status
from librarymodule.models import Library, Publication, Resources
from librarymodule.serializers import LibrarySerializer, PublicationSerializer, ResourcesSerializer
from core.views import IsAdmin, IsAuthenticated, LargeResultsSetPagination
from rest_framework.response import Response
from rest_framework import generics, filters
from django.db.models import Q
import datetime
import logging

db_logger = logging.getLogger('db')


# Create your views here.
class LibraryView(viewsets.ModelViewSet):
    queryset = Library.objects.all().order_by('created_time')
    serializer_class = LibrarySerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Library created successfully, library_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("Record added successfully!")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Library updated successfully, library_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Record updated successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Library deleted successfully, library_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            if instance.file:
                instance.file.storage.delete(instance.file.name)
            instance.delete()
            return Response("Record deleted successfully!")
        else:
            return Response({
                'message': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)


class PublicationView(viewsets.ModelViewSet):
    queryset = Publication.objects.all().order_by('created_time')
    serializer_class = PublicationSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Publication created successfully, publication_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("Record added successfully!")

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
             'message': f"Publication updated successfully, publication_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Record updated successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Publication deleted successfully, publication_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            if instance.file:
                instance.file.storage.delete(instance.file.name)
            instance.delete()
            return Response("Record deleted successfully!")
        else:
            return Response({
                'message': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ResourcesView(viewsets.ModelViewSet):
    queryset = Resources.objects.all().order_by('created_time')
    serializer_class = ResourcesSerializer
    permission_classes = (IsAuthenticated, IsAdmin,)
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Resources created successfully, resources_id:{serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("Record added successfully!")

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
             'message': f"Resources updated successfully, resources_id:{instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Record updated successfully")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Resources deleted successfully, resources_id:{instance.id}",
                            'status': status.HTTP_200_OK})
            if instance.image:
                instance.image.storage.delete(instance.image.name)
            if instance.file:
                instance.file.storage.delete(instance.file.name)
            instance.delete()
            return Response("Record deleted successfully!")
        else:
            return Response({
                'message': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)


class LibraryList(generics.ListAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get('filtertype'):
            search_status_list = request.GET.get('filtertype').split(',')
            queryset = queryset.filter(type__in=search_status_list)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PublicationList(generics.ListAPIView):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get('filtertype'):
            search_status_list = request.GET.get('filtertype').split(',')
            if 'Book' in search_status_list or 'Magazines' in search_status_list or 'Multimedia' in search_status_list \
                    or 'Others' in search_status_list:
                queryset = queryset.filter(type__in=search_status_list)
            else:
                return Response('Invalid filter type', status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ResourcesList(generics.ListAPIView):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.GET.get('filtertype'):
            search_status_list = request.GET.get('filtertype').split(',')
            if 'Video' in search_status_list or 'Audio' in search_status_list or 'Document' in search_status_list:
                queryset = queryset.filter(type__in=search_status_list)
            else:
                return Response('Invalid filter type', status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

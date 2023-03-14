from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from classmodule.models import Message
from classmodule.serializers import MessageSerializer, ClassSerializer
from core.views import LargeResultsSetPagination, IsAdmin, IsAdminOrTeacher
from classmodule.models import Class, Attendance
from rest_framework.response import Response
import datetime
from studentmodule.serializers import StudentSerializer
from studentmodule.models import Student
from .serializers import ClassLastMessageSerializer, AttendanceSerializer, AttendanceStudentSerializer
from rest_framework import filters
from datetime import datetime
from datetime import date
from datetime import timedelta
# import datetime
import logging

db_logger = logging.getLogger('db')


# Create your views here.
class MessageView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    queryset = Message.objects.all().order_by('-id')
    serializer_class = MessageSerializer

    def create(self, request, pk, *args, **kwargs):
        user = request.user
        class_check = Class.objects.filter(id=pk).first()

        if class_check:
            if user.role == 'teacher':
                id1 = class_check.teacher.user.id
                id2 = request.user.id
                if id1 == id2:

                    data = request.data

                    data['sender'] = class_check.teacher.user.id

                    data['class_id'] = pk

                    serializer = MessageSerializer(data=data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

                        return Response(serializer.data, status=status.HTTP_200_OK)
            if user.role == 'student':
                user_i = class_check.student_list.filter(id=user.studentuser.id).first()
                if user_i:
                    data = request.data
                    data['sender'] = user_i.user.id
                    data['class_id'] = pk
                    serializer = MessageSerializer(data=data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()

                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("This user is not a part of this class this class",
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("This user can't access this class", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("This class doesn't exist", status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        msgs = self.queryset.filter(class_id=kwargs['pk'])
        class_check = Class.objects.filter(id=kwargs['pk']).first()
        user = request.user
        if user.role == 'admin':
            queryset = self.filter_queryset(msgs)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(msgs, many=True)
            return Response(serializer.data)
        elif user.role == 'teacher':
            if user.id == class_check.teacher.user.id:
                queryset = self.filter_queryset(msgs)
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(msgs, many=True)
                return Response(serializer.data)
            else:
                return Response("This user is not a part of this class", status=status.HTTP_400_BAD_REQUEST)
        elif user.role == 'student':
            user_i = class_check.student_list.filter(id=user.studentuser.id).first()
            if user_i:
                queryset = self.filter_queryset(msgs)
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(msgs, many=True)
                return Response(serializer.data)
            else:
                return Response("You are not a part of this class", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("This user can't access this chat", status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def userAllChats(request, *args, **kwargs):
        user = request.user
        if user.role == 'student':
            classes = Class.objects.filter(student_list=user.studentuser)
            if request.GET.get('searchText'):
                search_text = request.GET.get('searchText')
                all_objs = classes.filter(title__icontains=search_text)
                serializer = ClassLastMessageSerializer(all_objs, many=True).data
            else:
                serializer = ClassLastMessageSerializer(classes, many=True).data
            return Response(serializer, status=status.HTTP_200_OK)
        elif user.role == 'teacher':
            classes = Class.objects.filter(teacher=user.teacheruser)
            if request.GET.get('searchText'):
                search_text = request.GET.get('searchText')
                all_objs = classes.filter(title__icontains=search_text)
                serializer = ClassLastMessageSerializer(all_objs, many=True).data
            else:
                serializer = ClassLastMessageSerializer(classes, many=True).data
            return Response(serializer, status=status.HTTP_200_OK)
        else:
            return Response("data not found", status=status.HTTP_400_BAD_REQUEST)

    # def classDetails(self, request, *args, **kwargs):
    #     Cl = Class.objects.filter(id=kwargs['pk'])
    #     result = Cl.values('id', 'title', 'status')
    #     return Response(result)
    def classDetails(self, request, *args, **kwargs):
        instance = Class.objects.filter(id=kwargs['pk']).first()
        response = ClassSerializer(instance).data
        return Response(response)


class ClassView(viewsets.ModelViewSet):
    queryset = Class.objects.all().order_by('created_time')
    serializer_class = ClassSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'status']
    pagination_class = LargeResultsSetPagination

    def create(self, request, *args, **kwargs):
        now_date = datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.now().strftime("%H:%M:%S")
        if datetime.strptime(request.data['startDate'], '%Y-%m-%d') > datetime.strptime(request.data['endDate'],
                                                                                        '%Y-%m-%d'):
            db_logger.error({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                             'Date': now_date, 'Time': now_time,
                             'message': "End date should greater than start date",
                             'status': status.HTTP_400_BAD_REQUEST})
            return Response('End date should greater than start date', status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Class created successfully, class_id: {serializer.data['id']}",
             'status': status.HTTP_201_CREATED})
        return Response("Record added successfully!")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        now_date = datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.now().strftime("%H:%M:%S")
        db_logger.info(
            {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email, 'Date': now_date,
             'Time': now_time,
             'message': f"Update class successfully, class_id: {instance.id}",
             'status': status.HTTP_200_OK})
        return Response("Record updated successfully")

    def change_class_status(self, request, pk):
        instance = self.get_object()
        if request.data['status']:
            now_date = datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.now().strftime("%H:%M:%S")
            db_logger.info({'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                            'Date': now_date, 'Time': now_time,
                            'message': f"Change class status to {request.data['status']}, class_id: {instance.id}",
                            'status': status.HTTP_200_OK})
            instance.status = request.data['status']
            instance.save()
            return Response("Status updated successfully")
        else:
            return Response("Status not found")

    def get_class_all_details(self, request, pk):
        instance = self.get_object()
        if instance:
            response = ClassSerializer(instance).data
            if instance.student_list.all():
                student_data = StudentSerializer(instance.student_list.all(), many=True).data
                if student_data:
                    return Response({'class': response, 'students': student_data})
            return Response({'class': response, 'students': []})
        else:
            return Response('not any detail found')

    def get_all_students_enroll(self, request, pk):
        check_class = self.queryset.filter(id=pk).first()
        if check_class:
            student_ids = check_class.student_list.filter().values_list('id', flat=True)
            all_objs = Student.objects.exclude(id__in=student_ids)
            response = StudentSerializer(all_objs, many=True).data
            return Response(response)
        else:
            return Response('class not found')

    def add_student_in_class(self, request, pk):
        now_date = datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.now().strftime("%H:%M:%S")
        check_class = self.queryset.filter(id=pk).first()
        if check_class:
            check_student = Student.objects.filter(id=request.data['student']).first()
            if check_student in check_class.student_list.all():
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date, 'Time': now_time,
                     'message': f"Student already exist in class, class_id: {check_class.id}, student_id: {check_student.id}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response({
                    'message': 'Student already exist in class'
                }, status=status.HTTP_400_BAD_REQUEST)
            get_student = Student.objects.filter(id=request.data['student']).first()
            if get_student:
                try:
                    db_logger.info(
                        {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                         'Date': now_date, 'Time': now_time,
                         'message': f"Student added in class, class_id: {check_class.id}, student_id: {get_student.id}",
                         'status': status.HTTP_200_OK})
                    check_class.student_list.add(get_student)
                    check_class.save()
                    return Response("Class assigned to students successfully")
                except Exception as e:
                    now_date = datetime.datetime.now().strftime("%d-%m-%Y")
                    now_time = datetime.datetime.now().strftime("%H:%M:%S")
                    db_logger.error(
                        {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                         'Date': now_date, 'Time': now_time,
                         'message': f"{e}, class_id: {check_class.id}, student_id: {get_student.id}",
                         'status': status.HTTP_400_BAD_REQUEST})
                    return Response(e)
            else:
                return Response("Student not found")
        else:
            return Response("Class not found")

    def remove_student_from_class(self, request):
        check_class = self.queryset.filter(id=request.data['classId']).first()
        if check_class:
            now_date = datetime.now().strftime("%d-%m-%Y")
            now_time = datetime.now().strftime("%H:%M:%S")
            check_student = Student.objects.filter(id=request.data['student']).first()
            if check_student:
                student_in_class = check_class.student_list.filter(id=check_student.id).first()
                if student_in_class:
                    check_class.student_list.remove(student_in_class)
                    check_class.save()
                    db_logger.info(
                        {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                         'Date': now_date, 'Time': now_time,
                         'message': f"student remove from class, class_id: {check_class.id}, student_id: {check_student.id}",
                         'status': status.HTTP_200_OK})
                    return Response("Removed successfully!")
                return Response("Student not found")
            else:
                return Response("Student not found")
        else:
            return Response("Class not found")


class AttendanceView(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated, IsAdminOrTeacher,)

    def create(self, request, *args, **kwargs):
        now_date_db = datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.now().strftime("%H:%M:%S")
        check_class = Class.objects.filter(id=kwargs['pk']).first()
        if check_class:
            tmp_date = date.today()
            now_date = datetime(tmp_date.year, tmp_date.month, tmp_date.day)
            req_date = datetime.strptime(request.data['date'], '%d/%m/%Y')
            check_attendance = self.queryset.filter(class_id=check_class, attendance_date=req_date)
            if check_attendance.exists():
                db_logger.error(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date_db, 'Time': now_time,
                     'message': f"Today attendance for this class already set, class_id:{check_class.id}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response('Today attendance for this class already set',
                                status=status.HTTP_400_BAD_REQUEST)
            if req_date > now_date:
                return Response('You can not set future date present', status=status.HTTP_400_BAD_REQUEST)
            check_previous_date = now_date - timedelta(days=10)
            if req_date < check_previous_date:
                return Response('You can not add 10 days late attendance', status=status.HTTP_400_BAD_REQUEST)
            try:
                students_list = []
                data = request.data
                for val in data['students']:
                    student_user = Student.objects.filter(id=val['id']).first()
                    if student_user and student_user in check_class.student_list.all():
                        students_list.append(
                            Attendance(class_id=check_class, student=student_user,
                                       attendance_type=val['attendance_type'],
                                       attendance_date=req_date, created_by=request.user)
                        )
                Attendance.objects.bulk_create(students_list)
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date_db, 'Time': now_time,
                     'message': f"Attendance saved successfully, class_id:{check_class.id}",
                     'status': status.HTTP_200_OK})
                return Response(
                    'Attendance saved successfully', status=status.HTTP_201_CREATED)
            except Exception as e:
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date_db, 'Time': now_time,
                     'message': f"{e}, class_id:{check_class.id}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Class not found', status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        now_date_db = datetime.now().strftime("%d-%m-%Y")
        now_time = datetime.now().strftime("%H:%M:%S")
        check_class = Class.objects.filter(id=kwargs['pk']).first()
        if check_class:
            tmp_date = date.today()
            now_date = datetime(tmp_date.year, tmp_date.month, tmp_date.day)
            req_date = datetime.strptime(request.data['date'], '%d/%m/%Y')
            if req_date > now_date:
                return Response('You can not set next days attendance', status=status.HTTP_400_BAD_REQUEST)
            check_previous_date = now_date - timedelta(days=10)
            if req_date < check_previous_date:
                return Response('you can not add 10 days late attendance', status=status.HTTP_400_BAD_REQUEST)
            try:
                create_students_list = []
                update_students_list = []
                data = request.data
                for val in data['students']:
                    student_user = self.queryset.filter(student=val['id'], class_id=check_class,
                                                        attendance_date=req_date).first()
                    if student_user:
                        student_user.attendance_type = val['attendance_type']
                        update_students_list.append(student_user)
                    else:
                        check_user = Student.objects.filter(id=val['id']).first()
                        if check_user and check_user in check_class.student_list.all():
                            create_students_list.append(
                                Attendance(class_id=check_class, student=check_user,
                                           attendance_type=val['attendance_type'],
                                           attendance_date=req_date, created_by=request.user)
                            )
                Attendance.objects.bulk_update(update_students_list, ['attendance_type'])
                if create_students_list:
                    Attendance.objects.bulk_create(create_students_list)
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date_db, 'Time': now_time,
                     'message': f"Attendance update successfully, class_id:{check_class.id}",
                     'status': status.HTTP_200_OK})
                return Response({
                    'Attendance update successfully'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                db_logger.info(
                    {'url': request.build_absolute_uri(), 'payload': request.data, 'user': request.user.email,
                     'Date': now_date_db, 'Time': now_time,
                     'message': f"{e}, class_id:{check_class.id}",
                     'status': status.HTTP_400_BAD_REQUEST})
                return Response(e)
        else:
            return Response('Class not found')

    def get_stats_attendance(self, request, pk):
        check_class = Class.objects.filter(id=pk).first()
        if check_class:
            req_month = request.GET.get('month')
            req_year = request.GET.get('year')
            if req_month and req_year:
                final_response = []
                get_instance = self.queryset.filter(attendance_date__year=req_year).filter(
                    attendance_date__month=req_month).filter(class_id=check_class).values(
                    "attendance_date").distinct()
                for _ in get_instance:
                    dict_data = {}
                    get_objs = self.queryset.filter(attendance_date=_['attendance_date'])
                    present_count = get_objs.filter(attendance_type='Present').count()
                    absent_count = get_objs.filter(attendance_type='Absent').count()
                    dict_data['title'] = f'Total Present {present_count}'
                    dict_data['start'] = _['attendance_date'].strftime('%Y-%m-%d')
                    final_response.append(dict_data)
                    dict_data = {'title': f'Total Absent {absent_count}',
                                 'start': _['attendance_date'].strftime('%Y-%m-%d')}
                    final_response.append(dict_data)
                return Response(final_response,
                                status=status.HTTP_200_OK)
            else:
                tmp_date = date.today()
                now_date = datetime(tmp_date.year, tmp_date.month, tmp_date.day)
                six_month_previous = now_date - timedelta(days=180)
                get_all_objs = self.queryset.filter(class_id=check_class).filter(
                    attendance_date__gte=six_month_previous).values(
                    "attendance_date").distinct()
                final_response = []
                for _ in get_all_objs:
                    dict_data = {}
                    get_objs = self.queryset.filter(attendance_date=_['attendance_date'])
                    present_count = get_objs.filter(attendance_type='Present').count()
                    absent_count = get_objs.filter(attendance_type='Absent').count()
                    dict_data['title'] = f'Total Present {present_count}'
                    dict_data['start'] = _['attendance_date'].strftime('%Y-%m-%d')
                    final_response.append(dict_data)
                    dict_data = {'title': f'Total Absent {absent_count}',
                                 'start': _['attendance_date'].strftime('%Y-%m-%d')}
                    final_response.append(dict_data)
                return Response(final_response)
        else:
            return Response('Class not found')

    def get_students_in_class(self, request, pk):
        check_class = Class.objects.filter(id=pk).first()
        if check_class:
            students_list = check_class.student_list.all()
            response = AttendanceStudentSerializer(students_list, context={'class_id': check_class,
                                                                           'date': datetime.strptime(
                                                                               request.GET.get('date'), '%d/%m/%Y'),
                                                                           'queryset': self.queryset
                                                                           }, many=True).data
            return Response(response)
        else:
            return Response('Class not found')

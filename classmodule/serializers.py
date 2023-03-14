from rest_framework import serializers
from classmodule.models import Class
from programmodule.serializers import CourseSerializer, TeacherCourseSerializer
from studentmodule.serializers import ClassStudentSerializer
from classmodule.models import Message, Attendance
from teachermodule.models import Teacher
from studentmodule.models import Student


class OnlyTeacherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)
    classes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"

    @staticmethod
    def get_email(obj):
        if obj.user:
            return obj.user.email
        return ''

    @staticmethod
    def get_classes(obj):
        get_teacher_classes = Class.objects.filter(teacher=obj)
        if get_teacher_classes:
            response_data = OnlyClassSerializer(get_teacher_classes, many=True).data
            return response_data
        return []


class ClassSerializer(serializers.ModelSerializer):
    teacher_details = serializers.SerializerMethodField(read_only=True)
    course_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"

    @staticmethod
    def get_teacher_details(obj):
        if obj.teacher:
            response = TeacherSerializer(obj.teacher).data
            return response
        return []

    @staticmethod
    def get_course_details(obj):
        if obj.course:
            response = CourseSerializer(obj.course).data
            return response
        return []


class OnlyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class ModifiedTecaherClassSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField(read_only=True)
    student_list = serializers.SerializerMethodField(read_only=True)
    teacher_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"

    @staticmethod
    def get_course(obj):
        response = TeacherCourseSerializer(obj.course).data
        return response

    @staticmethod
    def get_student_list(obj):
        response = ClassStudentSerializer(obj.student_list.all(), many=True).data
        return response

    @staticmethod
    def get_teacher_details(obj):
        response = OnlyTeacherDetailSerializer(obj.teacher).data
        return response


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = "__all__"

    @staticmethod
    def get_sender_name(obj):
        if obj.sender.role == 'student':
            return obj.sender.studentuser.firstname + ' ' + obj.sender.studentuser.lastname
        elif obj.sender.role == 'teacher':
            return obj.sender.teacheruser.firstname + ' ' + obj.sender.teacheruser.lastname
        elif obj.sender.role == 'admin':
            return obj.sender.adminuser.firstname + ' ' + obj.sender.adminuser.lastname
        return ''


class ClassLastMessageSerializer(serializers.ModelSerializer):
    teacher_details = serializers.SerializerMethodField(read_only=True)
    course_details = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"

    @staticmethod
    def get_teacher_details(obj):
        if obj.teacher:
            response = TeacherSerializer(obj.teacher).data
            return response
        return []

    @staticmethod
    def get_course_details(obj):
        if obj.course:
            response = CourseSerializer(obj.course).data
            return response
        return []

    @staticmethod
    def get_last_message(obj):
        response_mes = Message.objects.filter(class_id=obj).last()
        response = MessageSerializer(response_mes).data
        return response


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class AttendanceStudentSerializer(ReadOnlyModelSerializer):
    attendance_type = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = ["id", "firstname", "lastname", "email", "attendance_type"]

    @staticmethod
    def get_email(obj):
        if obj.user:
            return obj.user.email
        return ''

    def get_attendance_type(self, obj):
        objs = self.context['queryset'].filter(class_id=self.context['class_id'], student=obj,
                                               attendance_date=self.context['date']).first()
        if objs:
            return objs.attendance_type
        return 'Present'

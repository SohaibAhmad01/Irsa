from rest_framework import serializers
from teachermodule.models import Teacher
from classmodule.models import Class
from classmodule.serializers import OnlyClassSerializer, ModifiedTecaherClassSerializer
from studentmodule.serializers import StudentSerializer


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


class OnlyTeacherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"


class TeacherAllDataSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"

    @staticmethod
    def get_teacher(obj):
        teacher_all_data = {'teacher_detail': TeacherSerializer(obj).data}
        check_class = Class.objects.filter(teacher=obj)
        if check_class:
            teacher_all_data['classes'] = ModifiedTecaherClassSerializer(check_class, many=True).data
        else:
            teacher_all_data['classes'] = []
        return teacher_all_data


class StudentAllDataSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"

    @staticmethod
    def get_student(obj):
        student_all_data = {'student_detail': StudentSerializer(obj).data}
        check_class = Class.objects.filter(student_list=obj)
        if check_class:
            student_all_data['classes'] = ModifiedTecaherClassSerializer(check_class, many=True).data
        else:
            student_all_data['classes'] = []
        return student_all_data

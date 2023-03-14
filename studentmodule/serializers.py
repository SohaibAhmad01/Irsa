from rest_framework import serializers
from .models import Student
from programmodule.models import Programs, Course, CourseContent


class OnlyProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = "__all__"


class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    program_details = serializers.SerializerMethodField(read_only=True)
    course_content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    @staticmethod
    def get_course_content(obj):
        document_count = 0
        video_count = 0
        assignment_count = 0
        all_objects = CourseContent.objects.filter(course=obj)
        if all_objects:
            documents = all_objects.filter(type='VIDEO')
            video = all_objects.filter(type='DOCUMENT')
            assignment = all_objects.filter(type='ASSIGNMENT')
            if documents:
                document_count = len(documents)
            if video:
                video_count = len(video)
            if assignment:
                assignment_count = len(assignment)
            response = CourseContentSerializer(all_objects, many=True).data
            return {
                'result': response,
                'document_count': document_count,
                'video_count': video_count,
                'assignment_count': assignment_count,
            }
        return {}

    @staticmethod
    def get_program_details(obj):
        if obj.program:
            response = OnlyProgramSerializer(obj.program).data
            return response
        return []


class ProgramSerializer(serializers.ModelSerializer):
    courses_detail = serializers.SerializerMethodField(read_only=True)
    course_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Programs
        fields = "__all__"

    @staticmethod
    def get_courses_detail(obj):
        result = Course.objects.filter(program=obj.id)
        if result:
            response = CourseSerializer(result, many=True).data
            if response:
                return response
            return []
        return []

    @staticmethod
    def get_course_count(obj):
        result = Course.objects.filter(program=obj.id)
        if result:
            return len(result)
        return 0


class StudentSerializer(serializers.ModelSerializer):
    program_detail = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"

    @staticmethod
    def get_program_detail(obj):
        if obj.program:
            program_data = ProgramSerializer(obj.program).data
            if program_data:
                return program_data
            return {}
        return None

    @staticmethod
    def get_email(obj):
        if obj.user:
            return obj.user.email
        return ''


class ClassStudentSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"

    @staticmethod
    def get_email(obj):
        if obj.user:
            return obj.user.email
        return ''

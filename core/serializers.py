from rest_framework import serializers
from .models import User, News
from adminmodule.models import AdminUser
from teachermodule.serializers import TeacherSerializer
from studentmodule.serializers import StudentSerializer
from adminmodule.serializers import AdminUserSerializer


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    adminuser = AdminUserSerializer(read_only=True)
    studentuser = StudentSerializer(read_only=True)
    teacheruser = TeacherSerializer(read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}

from rest_framework import serializers
from .models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdminUser
        fields = "__all__"

    @staticmethod
    def get_role(obj):
        if obj.user:
            if obj.user.role == 'ADMIN':
                return 'Admin'
            return ''
        return ''

    @staticmethod
    def get_email(obj):
        if obj.user:
            return obj.user.email
        return ''

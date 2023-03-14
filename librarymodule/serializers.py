from rest_framework import serializers
from librarymodule.models import Library, Resources, Publication
import json


class LibrarySerializer(serializers.ModelSerializer):
    keywordss = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Library
        fields = "__all__"

    @staticmethod
    def get_keywordss(obj):
        if obj.keywords:
            return json.loads(obj.keywords[0])
        return []


class ResourcesSerializer(serializers.ModelSerializer):
    keywordss = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Resources
        fields = "__all__"

    @staticmethod
    def get_keywordss(obj):
        if obj.keywords:
            return json.loads(obj.keywords[0])
        return []


class PublicationSerializer(serializers.ModelSerializer):
    keywordss = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Publication
        fields = "__all__"

    @staticmethod
    def get_keywordss(obj):
        if obj.keywords:
            return json.loads(obj.keywords[0])
        return []

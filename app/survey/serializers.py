"""
Serializers for survey
"""
from rest_framework import serializers
from core.models import Survey

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
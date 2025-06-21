from rest_framework import serializers
from .models import *


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"



class RecommenderSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = Lecturer
        # Include only the fields you want to expose
        fields = ['name', 'workplace', 'email', 'full_name']
    
    def get_full_name(self, obj):
        # Assuming the full name is a combination of first and last name
        return f"{obj.name} - {obj.workplace}"

class LecturerSerializer(serializers.ModelSerializer):
    # Store the recommender details in a separate field
    recommender_details = RecommenderSerializer(
        source='recommender', read_only=True, required=False)
    subject_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Lecturer
        fields = "__all__"
    def get_subject_names(self, obj):
        return [subject.name for subject in obj.subjects.all()]

class LecturerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['id', 'status']

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['id', 'title', 'content', 'date', 'lecturer', 'type']
        
class ScheduleSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start = serializers.DateTimeField(source='start_time')
    end = serializers.DateTimeField(source='end_time')
    classNames = serializers.SerializerMethodField()
    
    def get_classNames(self, obj):
        return obj.subject.name if obj.subject else ""
    
    def get_title(self, obj):
        return str(obj)
    
    class Meta:
        model = Schedule
        fields = ("id", "start", "end", "title", 'classNames', 'lecturer', 'subject','place','notes')
        
class LecturerRecommendationSerializer(serializers.ModelSerializer):
    subject_names = serializers.SerializerMethodField()
    recommender_details = RecommenderSerializer(
        source='recommender', read_only=True, required=False)
    def get_subject_names(self, obj):
        return [subject.name for subject in obj.subjects.all()]
    class Meta:
        model = LecturerRecommendation
        fields = "__all__"
        read_only_fields = ['id', 'date']
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from lecturers.models import Lecturer
User = get_user_model()



class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        # Hides from the response when the user is created
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class NewUserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False
    )
    lecturer_str = serializers.SerializerMethodField()
    
    lecturer = serializers.PrimaryKeyRelatedField(
        queryset=Lecturer.objects.all(),
        required=False,
        allow_null=True
    )
        
    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        lecturer = validated_data.pop('lecturer', None)
        user = User.objects.create_user(**validated_data)
        if groups:
            user.groups.set(groups)
        if lecturer:
            # Check if this lecturer is already linked to a user
            if lecturer.user is not None:
                raise serializers.ValidationError("This lecturer is already linked to a user.")
            lecturer.user = user
            lecturer.save()
        return user
    
    def get_lecturer_str(self, obj):
        # If user has a related lecturer, return its __str__, else None
        lecturer = getattr(obj, 'lecturer', None)
        if lecturer:
            return str(lecturer)
        return None
    
    # Update the linked lecturer separately
    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        lecturer = validated_data.pop('lecturer', None)
        user = super().update(instance, validated_data)
        if groups is not None:
            user.groups.set(groups)
        if lecturer is not None:
            # Remove user from previous lecturer if exists
            try:
                old_lecturer = Lecturer.objects.get(user=user)
                old_lecturer.user = None
                old_lecturer.save()
            except Lecturer.DoesNotExist:
                pass
            lecturer.user = user
            lecturer.save()
        return user
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups', 'lecturer_str', 'lecturer', "password")
        extra_kwargs = {'password': {'write_only': True}}

        
class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for Group
    """

    class Meta:
        """
        Meta Class
        """

        model = Group
        fields = "__all__"
        
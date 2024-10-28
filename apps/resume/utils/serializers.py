""" Django Library """

from apps.authentification.utils.serializers import UserProfilesSerializer

""" Django Rest Framework Library """
from rest_framework import serializers

from apps.authentification.models import (
    ResumeUser,
    LevelEducation, JobCategories, JobApply, )


class JobCategoriessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories
        fields = ["id", "tag"]


class LevelsEducationSerialzier(serializers.ModelSerializer):
    class Meta:
        model = LevelEducation
        fields = "__all__"


class ResumesUserListSerializer(serializers.ModelSerializer):
    user = UserProfilesSerializer(read_only=True)
    job_tag = JobCategoriessListSerializer(read_only=True)
    level_of_education = LevelsEducationSerialzier(read_only=True)
    job_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ResumeUser
        fields = [
            "id",
            "user",
            "job_tag",
            "content",
            'job_count',
            "location",
            "date_of_brith",
            "phone",
            "level_of_education",
            "place_of_study",
            "position",
            "about",
            "job_experiences",
            "created_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Access the request from the serializer context
        request = self.context.get('request')

        # Modify the logo field to use the full URL
        if 'user' in representation and 'avatar' in representation['user']:
            logo_path = representation['user']['avatar']
            if logo_path and request:
                representation['user']['avatar'] = request.build_absolute_uri(logo_path)

        return representation

    def get_job_count(self, obj):
        filtering_data = JobApply.objects.select_related('resume').filter(
            resume=obj.id
        ).count()
        return filtering_data



class ResumeUserCreateSerializer(serializers.ModelSerializer):
    user = UserProfilesSerializer(read_only=True)

    class Meta:
        model = ResumeUser
        fields = [
            "id",
            "user",
            "job_tag",
            "content",
            "location",
            "date_of_brith",
            "phone",
            "level_of_education",
            "place_of_study",
            "position",
            "about",
            "job_experiences",
            "created_at",
        ]

    def create(self, validated_data):
        filtering_data = ResumeUser.objects.select_related('user').filter(
            user=self.context.get("user")
        ).count()
        if filtering_data >= 3:
            raise serializers.ValidationError({"error": "You may add no more than three resumes."})
        create = ResumeUser.objects.create(**validated_data)
        create.user = self.context.get("user")
        create.save()
        return create

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

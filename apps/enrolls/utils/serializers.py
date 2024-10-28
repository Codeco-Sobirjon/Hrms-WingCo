""" Django Libary """

""" Django Rest Framework Libary """
from rest_framework import serializers

from apps.authentification.models import (
    JobApply,
    JobCategories,
    JobVacancies,
    StatusApply,
    NotificationJobs,
    JobType,
    HrCompany,
    Favourites,
    Countries
)
from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)
from apps.company.utils.serializers import (
    HrCompanyListSerializer
)
from apps.resume.utils.serializers import (
    ResumesUserListSerializer
)


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = ['id', 'name', 'latitude', 'longitude', 'country']

    def create(self, validated_data):
        return Countries.objects.create(**validated_data)


class JobCategoriesListsSerializer(serializers.ModelSerializer):
    count_vacancy = serializers.SerializerMethodField()
    count_applied = serializers.SerializerMethodField()

    class Meta:
        model = JobCategories
        fields = ["id", "tag", "count_vacancy", "count_applied"]

    def get_count_applied(self, obj):
        category_id = obj.id
        filtering_data = JobApply.objects.filter(
            jobs__job_category__id=category_id
        ).count()
        return filtering_data

    def get_count_vacancy(self, obj):
        filtering_data = JobVacancies.objects.select_related('job_category').filter(
            job_category__id=obj.id
        ).count()
        return filtering_data


class JobCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories
        fields = ["id", "tag"]

    def create(self, validated_data):
        create = JobCategories.objects.create(**validated_data)
        return create

    def update(self, instance, validated_data):
        instance.tag = validated_data.get("tag", instance.tag)
        instance.save()
        return instance


class JobApplySerilaizer(serializers.ModelSerializer):
    user = UserProfilesSerializer(read_only=True)
    apply_jobs_user = UserProfilesSerializer(read_only=True, many=True)

    class Meta:
        model = JobApply
        fields = ["id", "user", "jobs", "apply_jobs_user", "created_at"]

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


class JobTypeSerialzier(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = '__all__'


class JobVacanciesListSerializer(serializers.ModelSerializer):
    job_category = JobCategoriesListSerializer(read_only=True)
    is_applied = serializers.SerializerMethodField()
    applied_count = serializers.SerializerMethodField()
    viewer_count = serializers.SerializerMethodField()
    looked_count = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_status = serializers.SerializerMethodField()
    company = HrCompanyListSerializer(read_only=True)
    job_type = JobTypeSerialzier(read_only=True)

    class Meta:
        model = JobVacancies
        fields = [
            "id",
            "job_category",
            "applied_count",
            "viewer_count",
            "looked_count",
            "favorite_count",
            'is_status',
            "is_favorite",
            'is_applied',
            "title",
            'level',
            'skills',
            "description",
            'qualifications',
            "salary",
            'job_type',
            'company',
            'experience',
            'work_hours',
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Access the request from the serializer context
        request = self.context.get('request')

        # Modify the logo field to use the full URL
        if 'company' in representation and 'logo' in representation['company']:
            logo_path = representation['company']['logo']
            if logo_path and request:
                representation['company']['logo'] = request.build_absolute_uri(logo_path)

        return representation

    def get_applied_count(self, obj):
        return obj.jobs.count()

    def get_favorite_count(self, obj):
        filtering_data = Favourites.objects.select_related('jobs').filter(
            jobs=obj.id
        ).count()
        return filtering_data

    def get_is_status(self, obj):
        user = self.context.get('user')
        user_applied = JobApply.objects.filter(
            user=user
        )
        if user_applied.filter(jobs_id=obj.id).exists():
            status = user_applied.values('jobs_status__name').first()
            return status['jobs_status__name']
        return False

    def get_viewer_count(self, obj):
        return obj.is_seen.count()

    def get_looked_count(self, obj):
        return obj.is_look_user.count()

    def get_is_favorite(self, obj):
        user = self.context.get('user')
        user_favorities = Favourites.objects.filter(
            user=user
        )
        if user_favorities.filter(jobs__id=obj.id).exists():
            return True
        return False
    
    def get_is_applied(self, obj):
        user = self.context.get('user')
        user_applied = JobApply.objects.select_related('user').filter(
            user=user
        )
        if user_applied.filter(jobs__id=obj.id).exists():
            return True
        return False


class JobVacanciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobVacancies
        fields = [
            "id",
            "job_category",
            "title",
            "description",
            "salary",
            'job_type',
            'company',
            'level',
            'skills',
            'experience',
            'qualifications',
            'work_hours',
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "job_category": {"required": True},
            "title": {"required": True},
            "description": {"required": True},
            "level": {"required": True},
            "job_type": {"required": True},
            "skills": {"required": True},
            "experience": {"required": True},
            "qualifications": {"required": True},
            "work_hours": {"required": True},
            "salary": {"required": True},
            "company": {"required": True},
        }

    def create(self, validated_data):
        user = self.context.get('user')
        if str(user.groups.all()[0]) == 'user' or str(user.groups.all()[0]) == 'admin':
            raise serializers.ValidationError(
                {'error': f"We can't to create job using {str(user.groups.all()[0])} role, try again hr role "})
        create = JobVacancies.objects.create(**validated_data)
        return create

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class StatusJobSerialzier(serializers.ModelSerializer):
    class Meta:
        model = StatusApply
        fields = "__all__"


class JobApplyListSerilaizer(serializers.ModelSerializer):
    job = JobVacanciesListSerializer(read_only=True, source='jobs')
    user = UserProfilesSerializer(read_only=True)
    jobs_status = StatusJobSerialzier(read_only=True)
    resume = ResumesUserListSerializer(read_only=True)

    class Meta:
        model = JobApply
        fields = [
            'id',
            'user',
            'job',
            'resume',
            'jobs_status',
            'created_at'
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

        # Check if the job is in the user's favorites
        if 'job' in representation and request:
            user_favorites = Favourites.objects.filter(user=request.user, jobs=representation['job']['id'])
            representation['job']['is_favorite'] = user_favorites.exists()

        if 'job' in representation and request:
            user_favorites = JobApply.objects.filter(user=request.user, jobs=representation['job']['id'])
            representation['job']['is_applied'] = user_favorites.exists()

        if 'job' in representation and request:
            user_favorites = JobApply.objects.filter(user=request.user, jobs=representation['job']['id'])
            if user_favorites.exists():
                status = user_favorites.values('jobs_status__name').first()
                representation['job']['is_status'] = status['jobs_status__name']

        return representation


class NotificationJobsSerialzier(serializers.ModelSerializer):
    jobs_status = StatusJobSerialzier(read_only=True)
    job_apply = JobApplyListSerilaizer(read_only=True)
    user = UserProfilesSerializer(read_only=True)

    class Meta:
        model = NotificationJobs
        fields = [
            'id',
            'job_apply',
            'jobs_status',
            'is_seen',
            'user',
            "created_at"
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


class JobApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApply
        fields = [
            'id',
            'user',
            'jobs',
            'jobs_status',
            'resume',
            'created_at'
        ]
        extra_kwargs = {
            "jobs": {"required": True},
            "resume": {"required": True},
        }

    def validate(self, data):
        jobs = data.get('jobs')
        resume = data.get('resume')
        if not jobs and not resume:
            raise serializers.ValidationError("one of jobs or resume number required")
        return data

    def create(self, validated_data):
        user = self.context.get('user')
        if JobApply.objects.filter(resume=validated_data['resume'], user=user, jobs=validated_data['jobs']).exists():
            raise serializers.ValidationError({'error': "You have already applied for this job."})

        create = JobApply.objects.create(**validated_data)
        create.user = self.context.get('user')
        create.save()
        add_user_company = HrCompany.objects.filter(
            id=create.jobs.company.id
        ).first()

        add_user_company.users.add(self.context.get('user').id)
        add_user_company.save()
        create_notification = NotificationJobs.objects.create()
        create_notification.job_apply = create
        create_notification.jobs_status = create.jobs_status
        create_notification.user = create.user
        create_notification.save()

        return create


class NotificationJobsSerializer(serializers.ModelSerializer):
    jobs_status = StatusJobSerialzier(read_only=True)
    job_apply = JobApplyListSerilaizer(read_only=True)

    class Meta:
        model = NotificationJobs
        fields = [
            'id',
            'job_apply',
            'jobs_status',
            'is_seen',
            'user',
            "created_at"
        ]


class FavouritesListSerializer(serializers.ModelSerializer):
    user = UserProfilesSerializer(read_only=True)
    jobs = JobVacanciesListSerializer(read_only=True)

    class Meta:
        model = Favourites
        fields = [
            'id',
            'user',
            'jobs',
            'created_at'
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


class FavouritesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourites
        fields = [
            'id',
            'user',
            'jobs',
            'created_at'
        ]

    def create(self, validated_data):
        create = Favourites.objects.create(**validated_data)
        create.user = self.context.get('user')
        create.jobs = self.context.get('job')
        create.save()
        return create
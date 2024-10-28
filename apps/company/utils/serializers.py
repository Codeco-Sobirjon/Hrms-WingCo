""" Django Library """
import json

from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers

from apps.authentification.models import HrCompany, Countries, JobVacancies, CompanyReview
from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)

def validate_file_size(value):
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(
            (f'File size must be no more than 2 mb.'),
            params={'max_size': max_size},
        )


class CountriessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = "__all__"


class SubHrCompanyListSerializer(serializers.ModelSerializer):
    countries = CountriessSerializer(read_only=True, many=True)

    class Meta:
        model = HrCompany
        fields = [
            "id",
            "name",
            "logo",
            "content",
            "countries",
            "created_at",
            "sub_company",
        ]


class HrCompanyListSerializer(serializers.ModelSerializer):
    hrs = UserProfilesSerializer(read_only=True, many=True)
    countries = CountriessSerializer(read_only=True, many=True)
    user_count = serializers.SerializerMethodField()
    job_count = serializers.SerializerMethodField()
    hrs_count = serializers.SerializerMethodField()


    class Meta:
        model = HrCompany
        fields = [
            "id",
            "name",
            "logo",
            "content",
            "countries",
            "hrs",
            "user_count",
            "hrs_count",
            "job_count",
            "created_at",
        ]

    def get_user_count(self, obj):
        return obj.users.count()

    def get_hrs_count(self, obj):
        return obj.hrs.count()

    def get_job_count(self, obj):
        count_jobs = (
            JobVacancies.objects.select_related("company")
            .filter(Q(company__id=obj.id))
            .count()
        )
        return count_jobs

def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')


class HrCompanyCreateSerializer(serializers.ModelSerializer):
    countries = CountriessSerializer(many=True, read_only=True)
    name = serializers.CharField(max_length=255, validators=[required])
    logo = serializers.FileField(
        max_length=None,
        allow_empty_file=False,
        use_url=True,
        required=True,
        validators=[validate_file_size]
    )
    content = serializers.CharField(max_length=255, validators=[required])


    class Meta:
        model = HrCompany
        fields = [
            "id",
            "name",
            "logo",
            "content",
            "countries",
            "hrs",
            "created_at",
        ]
        extra_kwargs = {
            "name": {"required": True},
            "logo": {"required": True},
            "content": {"required": True},
        }


    def create(self, validated_data):
        multiple_countries = json.loads(self.context.get("multiple_countries"))

        company = self.context.get("company")

        check_company_name = HrCompany.objects.filter(
            name=validated_data["name"]
        ).exists()

        if check_company_name:
            raise ValueError(
                {"msg": f"This company name {validated_data['name']} already exists"}
            )

        hr_company = HrCompany.objects.create(
            name=validated_data["name"],
            logo=self.context.get('logo'),
            content=validated_data["content"],
        )

        for country_id in multiple_countries:
            country_exists = Countries.objects.filter(id=country_id).exists()
            if not country_exists:
                raise serializers.ValidationError(
                    {"error": f"Country with ID {country_id} does not exist"}
                )

            hr_company.countries.add(country_id)

        hr_company.author = self.context.get("user")
        hr_company.hrs.add(self.context.get("user"))
        hr_company.save()

        if company:
            if not isinstance(company, HrCompany):
                company = HrCompany.objects.get(id=company)
            hr_company.sub_company = company
            hr_company.save()

        return hr_company

    def update(self, instance, validated_data):
        logo = self.context.get('logo')
        if self.context.get("multiple_countries"):
            multiple_countries = json.loads(self.context.get("multiple_countries"))

            for country_id in multiple_countries:
                country_exists = Countries.objects.filter(id=country_id).exists()
                if not country_exists:
                    raise serializers.ValidationError(
                        {"error": f"Country with ID {country_id} does not exist"}
                    )
                instance.countries.add(country_id)

        if 'name' in validated_data:
            check_company_name = HrCompany.objects.filter(
                name=validated_data["name"]
            ).exists()

            if check_company_name:
                raise serializers.ValidationError(
                    {"msg": f"This company name {validated_data['name']} already exists"}
                )
            instance.name = validated_data['name']

        if logo:
            instance.logo = logo

        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


class CompanyReviewListSerializers(serializers.ModelSerializer):
    user = UserProfilesSerializer(read_only=True)
    company = HrCompanyListSerializer(read_only=True)

    class Meta:
        model = CompanyReview
        fields = ['id', 'user', 'company', 'comment', 'created_at']


class CompanyReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyReview
        fields = ['id', 'user', 'company', 'comment', 'created_at']

    def create(self, validated_data):
        filtering_data = CompanyReview.objects.select_related('user').filter(
            user=self.context.get('user'), company=self.context.get('company')
        ).count()
        if filtering_data >= 1:
            raise serializers.ValidationError({"error": "You cannot write more than one comment"})
        create = CompanyReview.objects.create(**validated_data)
        create.user = self.context.get('user')
        create.company = self.context.get('company')
        create.save()
        return create

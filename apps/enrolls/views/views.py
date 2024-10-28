import random
import string

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    Countries,
    Favourites,
    JobApply,
    JobCategories,
    JobVacancies,
    NotificationJobs,
)
from apps.authentification.models import ResumeUser
from services.pagination_method import Pagination
from services.renderers import UserRenderers
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import (
    CountriesSerializer,
    FavouritesCreateSerializer,
    FavouritesListSerializer,
    JobApplyListSerilaizer,
    JobVacanciesListSerializer,
    NotificationJobsSerialzier,
)
from apps.resume.utils.serializers import ResumesUserListSerializer


def password_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class CountriesView(APIView):
    @swagger_auto_schema(
        request=CountriesSerializer,
        responses={201: CountriesSerializer(many=True)},
        operation_description="Get countries",
    )
    def get(self, request):
        queryset = Countries.objects.all().order_by("-id")
        serializer = CountriesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetViewerView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=JobVacanciesListSerializer,
        responses={201: JobVacanciesListSerializer(many=True)},
        operation_description="Viewers enjoyed in jobs",
    )
    def put(self, request, id):
        if request.user.is_authenticated:
            queryset = get_object_or_404(JobVacancies, id=id)
            queryset.is_seen.add(request.user)
            queryset.save()
            serializer = JobVacanciesListSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND
            )


class NotificationSeenJobsView(APIView):
    def get(self, request, id):
        queryset = get_object_or_404(NotificationJobs, id=id)
        queryset.is_seen = True
        queryset.save()
        serialziers = NotificationJobsSerialzier(queryset)
        return Response(serialziers.data, status=status.HTTP_200_OK)


class UserJobView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = JobApplyListSerilaizer

    @swagger_auto_schema(
        request=JobApplyListSerilaizer,
        responses={201: JobApplyListSerilaizer(many=True)},
        operation_description="Job vacancies filter by user",
    )
    def get(self, request, format=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND
            )

        instance = (
            JobApply.objects.select_related("user")
            .filter(user=request.user)
            .order_by("-id")
        )
        page = super().paginate_queryset(instance)

        if page is not None:
            serializer = super().get_paginated_response(
                self.serializer_class(page, many=True).data
            )
        else:
            serializer = self.serializer_class(instance, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class HrResumeUserListSerializer(APIView, Pagination):
    pagination_class = StandardResultsSetPagination
    serializer_class = ResumesUserListSerializer

    @swagger_auto_schema(
        request=ResumesUserListSerializer,
        responses={201: ResumesUserListSerializer(many=True)},
        operation_description="Get hr's resumes",
    )
    def get(self, request, format=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Token Invalid"}, status=status.HTTP_401_UNAUTHORIZED
            )

        vacancies = JobApply.objects.all()
        instance = ResumeUser.objects.select_related("user").filter(
            Q(user__in=[i.user for i in vacancies])
        )

        page = super().paginate_queryset(instance)

        if page is not None:
            serializer = super().get_paginated_response(
                self.serializer_class(page, many=True).data
            )
        else:
            serializer = self.serializer_class(instance, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FilterResumesView(APIView):
    @swagger_auto_schema(
        request=ResumesUserListSerializer,
        responses={201: ResumesUserListSerializer(many=True)},
        operation_description="Resume filter by job categories",
    )
    def get(self, request, id):
        queryset = get_object_or_404(JobCategories, id=id)
        vacancies = JobApply.objects.all()

        filter_resume = [
            resume for vacancy in vacancies
            for resume in ResumeUser.objects.select_related("job_tag", "user")
            .filter(job_tag=queryset, user=vacancy.user)
        ]

        serializers = ResumesUserListSerializer(filter_resume, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class FavouriesListView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        request=FavouritesListSerializer,
        responses={201: FavouritesListSerializer(many=True)},
        operation_description="Favorites get",
    )
    def get(self, request):
        if request.user.is_authenticated:
            queryset = Favourites.objects.filter(user=request.user).values_list("jobs", flat=True)
            filter_data = JobVacancies.objects.filter(id__in=queryset) if queryset else []

            page = super().paginate_queryset(filter_data)
            serializer = (
                super().get_paginated_response(
                    JobVacanciesListSerializer(page, many=True, context={'user': request.user}).data)
                if page is not None
                else JobVacanciesListSerializer(filter_data, many=True)
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)


class FavouritesCreateView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="jobs", type=int),
        ],
    )
    @swagger_auto_schema(
        request=FavouritesCreateSerializer,
        responses={201: FavouritesCreateSerializer(many=True)},
        operation_description="Favorites create",
    )
    def post(self, request, id):
        expected_fields = {"jobs"}
        received_fields = set(request.data.keys())

        unexpected_fields = received_fields - expected_fields
        if unexpected_fields:
            error_message = (
                f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            )
            return Response(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)


        queryset = get_object_or_404(JobVacancies, id=id)
        if not queryset:
            return Response({"error": "No Vacancy"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FavouritesCreateSerializer(
            data=request.data, context={"user": request.user, "job": queryset}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if request.user.is_authenticated:
            queryset = get_object_or_404(JobVacancies, id=id)
            try:
                filtering_data = Favourites.objects.get(jobs=queryset, user=request.user)
                filtering_data.delete()
                return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                filtering_data = "No Vacancies for this ids"
                return Response({'error': filtering_data}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND
            )

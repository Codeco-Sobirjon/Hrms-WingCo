from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    JobApply,
    NotificationJobs,
    StatusApply, JobCategories,
)
from services.pagination_method import PaginationFunc
from services.renderers import UserRenderers
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import (
    JobApplyListSerilaizer,
    JobApplySerializer,
)


class AppllyJobView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=JobApplySerializer,
        responses={201: JobApplySerializer(many=True)},
        operation_description="Create job vacancies",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="jobs", type=int),
            OpenApiParameter(name="resume", type=str),
        ],
    )
    def post(self, request):
        expected_fields = {"jobs", "resume"}
        received_fields = set(request.data.keys())

        if unexpected_fields := received_fields - expected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        if not self.has_permission(request.user):
            return Response({"error": "You don't have permission to access this resource"}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobApplySerializer(
            data=request.data,
            context={"user": request.user},
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def has_permission(self, user):
        user_groups = user.groups.values_list('name', flat=True)
        return "hr" not in user_groups and "admin" not in user_groups


class ApplyJobAcceptOrRejectedView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def patch(self, request, id, status_id):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        if self.has_permission(request.user):
            return Response({"error": "You don't have permission to access this resource"}, status=status.HTTP_403_FORBIDDEN)


        queryset = get_object_or_404(JobApply, id=id)
        get_status_id = StatusApply.objects.filter(Q(id=status_id)).first()
        queryset.jobs_status = get_status_id
        queryset.save()

        create = NotificationJobs.objects.create(
            job_apply=queryset, jobs_status=get_status_id, user=queryset.user
        )

        serializer = JobApplyListSerilaizer(queryset, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def has_permission(self, user):
        user_groups = user.groups.values_list('name', flat=True)
        return "user" in user_groups or "admin" in user_groups


class ApplyJobDetailsView(APIView):
    @extend_schema(
        request=None, responses=JobApplyListSerilaizer, description="Apply job details"
    )
    def get(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        serializer = JobApplyListSerilaizer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        user_group = str(request.user.group.values_list('name', flat=True).first())

        if user_group == "user":
            queryset = get_object_or_404(JobApply, id=id)
            queryset.delete()
            return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "You can't delete with this role"})


class JobVacaniesFilterCategories(APIView, PaginationFunc):
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        request=JobApplyListSerilaizer,
        responses={201: JobApplyListSerilaizer(many=True)},
        operation_description="Job vacancies filter/search by id",
    )
    def get(self, request):
        id = request.query_params.get("id", None)
        jobs_status = request.query_params.get("status_id", None)
        if id:
            queryset = JobCategories.objects.get(id=id)
            queryset_job_filter = JobApply.objects.select_related("jobs").filter(
                Q(jobs__job_category=queryset)
            )
            serializer = super().page(queryset_job_filter, JobApplyListSerilaizer)
            return Response({"data": serializer.data, "count": queryset_job_filter.count()}, status=status.HTTP_200_OK)

        queryset = JobApply.objects.select_related("jobs_status").filter(
            jobs_status__id=jobs_status
        )
        serializer = super().page(queryset, JobApplyListSerilaizer)
        return Response(serializer.data, status=status.HTTP_200_OK)

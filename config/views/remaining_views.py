from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    Countries,
    JobApply,
    JobVacancies,
    NotificationJobs,
    ResumeUser,
)
from services.pagination_method import (
    Pagination
)
from services.renderers import UserRenderers
from apps.authentification.utils.serializers import (
    RoleSerializer
)
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import (
    CountriesSerializer,
    JobApplyListSerilaizer,
    NotificationJobsSerialzier,
)
from apps.resume.utils.serializers import (
    ResumesUserListSerializer,
    ResumeUserCreateSerializer,
)
from services.pagination_method import PaginationFunc

class RolesViews(APIView):
    @swagger_auto_schema(
        request=RoleSerializer,
        responses={201: RoleSerializer(many=True)},
        operation_description="Get roles",
    )
    def get(self, request):
        queryset = Group.objects.all()[1:3]
        serializer = RoleSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ApplyJobDetailsView(APIView):
    @extend_schema(
        request=None, responses=JobApplyListSerilaizer, description="Apply job details"
    )
    def get(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        serializer = JobApplyListSerilaizer(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        user_role = str(request.user.groups.values_list('name', flat=True).first())

        if user_role == "user":
            queryset = get_object_or_404(JobApply, id=id)
            queryset.delete()
            return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)

        raise PermissionDenied("You can't delete with this role")


class ResumeFilterView(APIView, PaginationFunc):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        request=JobApplyListSerilaizer,
        operation_description="Vacancies filter by resume",
    )
    def get(self, request, resumeID):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_object_or_404(ResumeUser, id=resumeID)
        instance = JobApply.objects.select_related("resume").filter(Q(resume=queryset))
        serializer = super().page(instance, JobApplyListSerilaizer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryGetViews(APIView):
    def get(self, request):
        queryset = Countries.objects.all().order_by("-id")
        serializer = CountriesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryCreateViews(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        if str(request.user.groups.all().first()) != "admin":
            return Response({"error": "You can't create a country with this role"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CountriesSerializer(data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HrResumeUserListSerializer(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = ResumesUserListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    @swagger_auto_schema(
        request=ResumesUserListSerializer,
        responses={201: ResumesUserListSerializer(many=True)},
        operation_description="Get hrs resumes",
    )
    def get(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            vacancies = JobVacancies.objects.get(
                id=id, company__hrs__email=request.user.email
            )
        except ObjectDoesNotExist:
            return Response(
                {"error": "No Vacancy for this HR"},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_apply_jobs = (
            JobApply.objects.select_related("jobs")
            .filter(Q(jobs=vacancies) & Q(jobs_status=2))
            .values("resume__user")
        )

        name = request.query_params.get("name", None)
        if bool(name):
            instance = (
                ResumeUser.objects.select_related("user")
                .filter(Q(user__in=filter_apply_jobs))
                .filter(user__username__icontains=name)
            )
        else:
            instance = ResumeUser.objects.select_related("user").filter(
                Q(user__in=filter_apply_jobs)
            )

        page = super().paginate_queryset(instance)
        if page is not None:
            serializer = super().get_paginated_response(
                self.serializer_class(page, many=True).data
            )
        else:
            serializer = self.serializer_class(instance, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResumeUserView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        request=ResumesUserListSerializer,
        operation_description="User resume get",
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        user_group_name = request.user.groups.values_list('name', flat=True).first()

        if user_group_name == "user":
            queryset = ResumeUser.objects.select_related("user").filter(Q(user=request.user)).order_by('-id')
        else:
            queryset = ResumeUser.objects.all().order_by("-id")

        page = super().paginate_queryset(queryset)
        serializer = (
            super().get_paginated_response(ResumesUserListSerializer(page, many=True, context={'request': request}).data)
            if page is not None
            else ResumesUserListSerializer(queryset, many=True, context={'request': request})
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request=ResumeUserCreateSerializer,
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="job_tag", type=str),
            OpenApiParameter(name="content", type=str),
            OpenApiParameter(name="location", type=str),
            OpenApiParameter(name="date_of_brith", type=str),
            OpenApiParameter(name="phone", type=str),
            OpenApiParameter(name="level_of_education", type=str),
            OpenApiParameter(name="place_of_study", type=str),
            OpenApiParameter(name="position", type=str),
            OpenApiParameter(name="about", type=str),
            OpenApiParameter(name="job_experiences", type=str),
        ],
        description="Create Resume",
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ResumeUserCreateSerializer(
            data=request.data, partial=True, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationJobsView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        user_role = str(request.user.groups.values_list('name', flat=True).first())
        if user_role == "user":
            queryset = (
                NotificationJobs.objects.select_related("user")
                .filter(Q(user=self.request.user))
                .filter(Q(is_seen=False)).filter(Q(jobs_status=2) | Q(jobs_status=3))
            ).order_by('-id')
            page = super().paginate_queryset(queryset)
            serializer = (
                super().get_paginated_response(NotificationJobsSerialzier(page, many=True, context={"request": self.request}).data)
                if page is not None
                else NotificationJobsSerialzier(queryset, many=True)
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        queryset = queryset = (
                NotificationJobs.objects.select_related("user")
                .filter(Q(job_apply__jobs__company__hrs=self.request.user))
                .filter(Q(is_seen=False)).filter(Q(jobs_status=1))
            ).order_by('-id')
        page = super().paginate_queryset(queryset)
        serializer = (
            super().get_paginated_response(NotificationJobsSerialzier(page, many=True, context={"request": self.request}).data)
            if page is not None
            else NotificationJobsSerialzier(queryset, many=True)
        )

        return Response(serializer.data, status=status.HTTP_200_OK)



class AppliedUsersHrView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        role_handlers = {
            "hr": self.get_applied_users_for_hr,
        }

        if request.user.is_authenticated:
            user_role = str(request.user.groups.values_list('name', flat=True).first())

            if user_role in role_handlers:
                return role_handlers[user_role](request)
            else:
                return Response({'error': f"Unsupported role: {user_role}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

    def get_applied_users_for_hr(self, request):
        queryset = JobApply.objects.filter(jobs__company__author=request.user)
        page = super().paginate_queryset(queryset)
        serializer = (
            super().get_paginated_response(JobApplyListSerilaizer(page, many=True).data)
            if page is not None
            else JobApplyListSerilaizer(queryset, many=True)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

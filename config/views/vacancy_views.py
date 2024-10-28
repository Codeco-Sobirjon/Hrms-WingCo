from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, ExpressionWrapper, FloatField

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    CustomUser,
    JobApply,
    JobVacancies,
    ResumeUser,
    Countries, Favourites
)


from services.pagination_method import (
    Pagination, PaginationFunc
)
from services.renderers import UserRenderers
from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import (
    JobVacanciesListSerializer,
    JobVacanciesSerializer,
)
from apps.resume.utils.serializers import (
    ResumesUserListSerializer,
)



class JobVacanciesView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "job_category",
        "title",
        "content",
        "salary",
        "country",
        "company",
    ]

    def get(self, request, format=None, *args, **kwargs):
        queryset = JobVacancies.objects.order_by('-id')
        if request.user.is_authenticated:
            queryset = self.filter_by_user_role(queryset, request)
            queryset = self.filter_by_location(queryset, request)
            queryset = self.filter_by_category(queryset, request)
            queryset = self.filter_by_salary(queryset, request)
            queryset = self.filter_by_title(queryset, request)
            queryset = self.filter_by_description(queryset, request)
            queryset = self.filter_by_country(queryset, request)
            queryset = self.filter_by_company(queryset, request)
            queryset = self.filter_by_is_applied(queryset, request)
            queryset = self.filter_by_is_favourite(queryset, request)
            queryset = self.sort_by_count(queryset, request)
            page = super().paginate_queryset(queryset.order_by('-id'))

            if page is not None:
                serializer = super().get_paginated_response(
                    JobVacanciesListSerializer(page, many=True, context={'user': request.user, 'request': request}).data
                )
            else:
                serializer = JobVacanciesListSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        page = super().paginate_queryset(queryset)
        if page is not None:
            serializer = super().get_paginated_response(
                JobVacanciesListSerializer(page, many=True, context={'request': request}).data
            )
        else:
            serializer = JobVacanciesListSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def filter_by_user_role(self, queryset, request):
        user_groups = request.user.groups.all()
        if user_groups.exists() and str(user_groups[0]) == "hr":
            queryset = queryset.filter(company__hrs=request.user)
        return queryset

    def filter_by_location(self, queryset, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if lat and lng:
            lat = float(lat)
            lng = float(lng)

            distance_expression = ExpressionWrapper(
                F('latitude') * F('latitude') +
                F('longitude') * F('longitude') -
                2 * F('latitude') * lat -
                2 * F('longitude') * lng +
                lat * lat +
                lng * lng,
                output_field=FloatField()
            )
            countries = Countries.objects.annotate(distance=distance_expression).filter(distance__lte=0.05).values(
                'country')
            queryset = queryset.filter(Q(company__countries__country__in=countries))
        return queryset

    def filter_by_category(self, queryset, request):
        category = request.query_params.get("category", [])
        if category:
            ids_category = [int(id_str) for id_str in category.split(",")]
            queryset = queryset.filter(Q(job_category__in=ids_category))
        return queryset

    def filter_by_salary(self, queryset, request):
        salary = request.query_params.get("salary", [])
        if salary:
            ids_salary = [int(id_str) for id_str in salary.split(",")]
            queryset = queryset.filter(Q(salary__gte=ids_salary[0]), Q(salary__lt=ids_salary[1]))
        return queryset

    def filter_by_title(self, queryset, request):
        title = request.query_params.get("title", None)
        if title:
            queryset = queryset.filter(Q(title__icontains=title))
        return queryset

    def filter_by_description(self, queryset, request):
        description = request.query_params.get("description", None)
        if description:
            queryset = queryset.filter(description__iexact=description)
        return queryset

    def filter_by_country(self, queryset, request):
        country = request.query_params.get("country", [])
        if country:
            ids_country = [id_str for id_str in country.split(",")]
            queryset = queryset.filter(
                Q(company__countries__name__icontains=ids_country[0])
                | Q(company__countries__id=int(ids_country[1]))
            )
        return queryset

    def filter_by_company(self, queryset, request):
        company = request.query_params.get("company", [])
        if company:
            ids_company = [id_str for id_str in company.split(",")]
            queryset = queryset.filter(
                Q(company__name__icontains=ids_company[0])
                | Q(company__id=int(ids_company[1]))
            )
        return queryset

    def filter_by_is_applied(self, queryset, request):
        is_applied = request.query_params.get('is_applied', None)

        if is_applied is not None:
            try:
                is_applied = int(is_applied)
                user_applied = JobApply.objects.select_related('user').filter(
                    user=request.user
                ).values('jobs__id')

                if is_applied == 1:
                    queryset = queryset.filter(id__in=user_applied)
                else:
                    queryset = queryset.exclude(id__in=user_applied)
            except ValueError:
                pass

        return queryset

    def filter_by_is_favourite(self, queryset, request):
        is_favourite = request.query_params.get('is_favorite', None)
        if is_favourite is not None:
            try:
                is_favourite = int(is_favourite)
                if is_favourite == 1:
                    user_favorites = Favourites.objects.filter(
                        user=request.user
                    ).values('jobs__id')
                    queryset = queryset.filter(id__in=user_favorites)
                else:
                    user_favorites = Favourites.objects.filter(
                        user=request.user
                    ).values('jobs__id')
                    queryset = queryset.exclude(id__in=user_favorites)
            except ValueError:
                pass

        return queryset

    def sort_by_count(self, queryset, request):
        order_by = request.query_params.get("sort", '')
        if order_by == 'desc':
            queryset = queryset.annotate(count=Count('jobs')).order_by('-count')
        else:
            queryset = queryset.annotate(count=Count('jobs')).order_by('count')
        return queryset

    @swagger_auto_schema(
        request=JobVacanciesSerializer,
        responses={201: JobVacanciesSerializer(many=True)},
        operation_description="Create job vacancies",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="job_category", type=int),
            OpenApiParameter(name="title", type=str),
            OpenApiParameter(name="description", type=str),
            OpenApiParameter(name="salary", type=float),
            OpenApiParameter(name="job_type", type=int),
            OpenApiParameter(name="company", type=int),
            OpenApiParameter(name="experience", type=int),
            OpenApiParameter(name="work_hours", type=int),
        ],
    )
    def post(self, request):
        expected_fields = {
            "job_category",
            "title",
            "description",
            "salary",
            "job_type",
            "company",
            "experience",
            "work_hours",
            'level',
            'skills',
            'qualifications',
        }
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        if unexpected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not self.has_permission(request.user):
            return Response({"error": "You don't have permission to access this resource"},
                            status=status.HTTP_403_FORBIDDEN)

        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = JobVacanciesSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def has_permission(self, user):
        user_groups = user.groups.values_list('name', flat=True)
        return "user" not in user_groups and "admin" not in user_groups


class JobVacanciesDetailsView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=JobVacanciesListSerializer,
        responses={201: JobVacanciesListSerializer(many=True)},
        operation_description="Job vacancies get",
    )
    def get(self, request, id):
        if not request.user.is_authenticated:
            queryset = get_object_or_404(JobVacancies, id=id)
            serializer = JobVacanciesListSerializer(queryset, context={"request": request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        queryset = get_object_or_404(JobVacancies, id=id)
        serializer = JobVacanciesListSerializer(queryset, context={"request": request, 'user': request.user})

        queryset.is_look_user.add(request.user)
        queryset.save()
        if request.user.groups.filter(name__in=["hr", "admin"]).exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "You don't have permission to access this resource"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request=JobVacanciesSerializer,
        responses={201: JobVacanciesSerializer(many=True)},
        operation_description="Job vacancies update",
    )
    def put(self, request, id):
        expected_fields = {
            "job_category",
            "title",
            "description",
            "salary",
            "job_type",
            "company",
            "experience",
            "work_hours",
            'level',
            'skills',
            'qualifications',
        }
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        if unexpected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = get_object_or_404(JobVacancies, id=id)
        serializer = JobVacanciesSerializer(instance=queryset, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = get_object_or_404(JobVacancies, id=id)
        queryset.delete()

        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


class JobVacancyCandidatesView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = UserProfilesSerializer
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
        if not bool(name):
            filter_resume = (
                ResumeUser.objects.select_related("user")
                .filter(Q(user__in=filter_apply_jobs))
                .values("user")
            )

            instance = CustomUser.objects.filter(id__in=filter_resume)
            page = super().paginate_queryset(instance)
            if page is not None:
                serializer = super().get_paginated_response(
                    self.serializer_class(page, many=True).data
                )
            else:
                serializer = self.serializer_class(instance, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        filter_resume = (
            ResumeUser.objects.select_related("user")
            .filter(Q(user__in=filter_apply_jobs))
            .values("user")
        )

        instance = CustomUser.objects.filter(id__in=filter_resume)
        page = super().paginate_queryset(instance)
        if page is not None:
            serializer = super().get_paginated_response(
                self.serializer_class(page, many=True).data
            )
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobVacancyResumeView(APIView, PaginationFunc):
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
        vacancies = get_object_or_404(JobVacancies, id=id, company__hrs=request.user)

        filter_apply_jobs = (
            JobApply.objects.select_related("jobs")
            .filter(Q(jobs=vacancies))
            .values("resume__user")
        )
        name = request.query_params.get("name", None)

        if not bool(name):
            instance = ResumeUser.objects.select_related("user").filter(
                Q(user__in=filter_apply_jobs)
            )
        else:
            instance = ResumeUser.objects.select_related("user").filter(
                Q(user__in=filter_apply_jobs) & Q(user__username__icontains=name)
            )

        serializer = super().page(instance, self.serializer_class)

        return Response(serializer.data, status=status.HTTP_200_OK)
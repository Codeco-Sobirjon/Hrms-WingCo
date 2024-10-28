from django.core.exceptions import PermissionDenied
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
    HrCompany,
    JobVacancies, CompanyReview,
)
from services.pagination_method import PaginationFunc
from services.renderers import UserRenderers
from apps.company.utils.serializers import (
    HrCompanyCreateSerializer,
    HrCompanyListSerializer, CompanyReviewListSerializers, CompanyReviewCreateSerializer

)
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import JobVacanciesListSerializer




class HrCompanyView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=HrCompanyCreateSerializer,
        responses={201: HrCompanyCreateSerializer},
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="name", type=str),
            OpenApiParameter(name="content", type=str),
            OpenApiParameter(name="logo", type=str),
            OpenApiParameter(name="countries", type=str),
            OpenApiParameter(name="sub_company", type=str),
        ],
        description="Create company",
    )
    def post(self, request):
        unexpected_fields = self.validate_fields(request.data)
        if unexpected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return self.invalid_token_response()

        multiple_countries = request.data.get("countries", [])
        serializers = self.get_serializer(data=request.data, context={"request": request, "user": request.user, 'multiple_countries': multiple_countries, 'logo': request.FILES.get('logo', None)})
        return self.process_serializer(serializers)

    def validate_fields(self, data):
        expected_fields = {"name", "content", "logo", "countries",}
        received_fields = set(data.keys())
        return received_fields - expected_fields

    def get_serializer(self, *args, **kwargs):
        return HrCompanyCreateSerializer(*args, **kwargs)

    def process_serializer(self, serializers):
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def invalid_token_response(self):
        return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)


class GetCompaniesView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=HrCompanyListSerializer,
        operation_description="Get company",
    )
    def get(self, request, id):
        if request.user.is_authenticated:
            queryset = get_object_or_404(HrCompany, id=id)
            serializers = HrCompanyListSerializer(queryset, context={"request": request})
            return Response(serializers.data, status=status.HTTP_200_OK)
        else:
            queryset = get_object_or_404(HrCompany, id=id)
            serializers = HrCompanyListSerializer(queryset, context={"request": request})
            return Response(serializers.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request=HrCompanyCreateSerializer,
        operation_description="Update company",
    )
    def put(self, request, id):
        if not request.user.is_authenticated:
            return self.invalid_token_response()

        queryset = get_object_or_404(HrCompany, id=id)

        if not self.user_has_hr_role(request.user):
            raise PermissionDenied("You can't update with this role")

        logo_file, multiple_countries = self.extract_request_data(request)

        updated_data = self.update_hr_company(queryset, request.data, logo_file, multiple_countries)

        return Response(updated_data, status=status.HTTP_200_OK)

    def invalid_token_response(self):
        return Response({"error": "Token Invalid"}, status=status.HTTP_401_UNAUTHORIZED)

    def user_has_hr_role(self, user):
        return str(user.groups.values_list('name', flat=True).first()) == 'hr'

    def extract_request_data(self, request):
        logo_file = request.FILES.get('logo', None)
        multiple_countries = request.data.get("countries", [])
        return logo_file, multiple_countries

    def update_hr_company(self, instance, data, logo, countries):
        serializer = HrCompanyCreateSerializer(
            instance=instance,
            data=data,
            partial=True,
            context={'request': self.request, 'logo': logo, 'multiple_countries': countries}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer.data

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return self.invalid_token_response()

        queryset = get_object_or_404(HrCompany, id=id)

        if not self.user_has_hr_role(request.user):
            raise PermissionDenied("You can't delete with this role")

        self.delete_hr_company(queryset)

        return Response({'msg': "Deleted successfully"})

    def invalid_token_response(self):
        return Response({"error": "Token Invalid"}, status=status.HTTP_401_UNAUTHORIZED)

    def user_has_hr_role(self, user):
        return str(user.groups.values_list('name', flat=True).first()) == 'hr'

    def delete_hr_company(self, instance):
        instance.delete()


class CompanyVacancies(APIView, PaginationFunc):
    pagination_class = StandardResultsSetPagination
    serializer_class = JobVacanciesListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    @swagger_auto_schema(
        request=JobVacanciesListSerializer,
        operation_description="Get company vacancies",
    )
    def get(self, request, id):
        queryset = get_object_or_404(HrCompany, id=id)
        name = request.query_params.get("name", None)

        instance = (
            JobVacancies.objects.select_related("company")
            .filter(Q(company=queryset), Q(is_activate=True))
            .filter(Q(title__icontains=name) if bool(name) else Q())
        ).order_by("-id")

        serializer = super().page(instance, JobVacanciesListSerializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyReviewListView(APIView, PaginationFunc):
    pagination_class = StandardResultsSetPagination

    def get(self, request, id):
        queryset = get_object_or_404(HrCompany, id=id)
        filtering_data = CompanyReview.objects.select_related('company').filter(
            company=queryset
        )
        serializer = super().page(filtering_data, CompanyReviewListSerializers)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyReviewCreateView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def post(self, request, id):
        if not request.user.is_authenticated:
            return self.invalid_token_response()

        user_role = str(request.user.groups.values_list('name', flat=True).first())

        if user_role == "user":
            queryset = get_object_or_404(HrCompany, id=id)

            serializer = self.create_review_serializer(request, queryset)

            return self.save_review(serializer)
        else:
            raise PermissionDenied("You can't create a review with this role")

    def invalid_token_response(self):
        return Response({"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)

    def create_review_serializer(self, request, hr_company):
        return CompanyReviewCreateSerializer(
            data=request.data,
            context={'user': request.user, 'company': hr_company}
        )

    def save_review(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

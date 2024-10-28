from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    CustomUser,
    HrCompany,
)
from services.pagination_method import (
    Pagination
)
from services.renderers import UserRenderers
from apps.authentification.utils.serializers import (
    UserProfilesSerializer
)
from apps.company.utils.serializers import (
    HrCompanyListSerializer,
)
from apps.enrolls.utils.pagination import StandardResultsSetPagination


class HrListView(APIView, Pagination):
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["name", "company"]

    @swagger_auto_schema(
        request=UserProfilesSerializer,
        operation_description="Get hrs",
    )
    def get(self, request):
        filters = {
            "name": self.filter_by_name,
            "company": self.filter_by_company,
        }

        queryset = self.base_queryset()

        for param, filter_func in filters.items():
            value = request.query_params.get(param)
            if bool(value):
                queryset = filter_func(queryset, value)

        page = super().paginate_queryset(queryset)

        if page is not None:
            serializer = super().get_paginated_response(
                UserProfilesSerializer(page, many=True, context={'request': request}).data
            )
        else:
            serializer = UserProfilesSerializer(queryset, many=True, context={'request': request})

        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def base_queryset(self):
        return CustomUser.objects.prefetch_related("groups") \
            .filter(groups__name__in=["hr"]) \
            .order_by("-id")

    def filter_by_name(self, queryset, value):
        return queryset.filter(first_name__icontains=value)

    def filter_by_company(self, queryset, value):
        try:
            company_filter = HrCompany.objects.get(id=value)
            return list(chain.from_iterable([ids.hrs.all() for ids in [company_filter]]))
        except ObjectDoesNotExist:
            return queryset


class HrCompanyAllView(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "country"]

    @swagger_auto_schema(
        request=HrCompanyListSerializer,
        operation_description="All gets hr companies ",
    )
    def get(self, request):
        search_name = request.query_params.get("name", None)
        country = request.query_params.get("country", None)

        if request.user.is_authenticated:
            queryset = self.get_authenticated_queryset(request, search_name, country)
        else:
            queryset = self.get_unauthenticated_queryset(request, search_name, country)

        page = super().paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, request)

        if page is not None:
            response_data = super().get_paginated_response(serializer.data)
        else:
            response_data = serializer

        return Response(response_data.data, status=status.HTTP_200_OK)

    def get_authenticated_queryset(self, request, search_name, country):
        queryset = HrCompany.objects.prefetch_related("hrs").filter(Q(hrs=request.user)).order_by("-id")

        if bool(search_name):
            queryset = queryset.filter(name__icontains=search_name)

        return queryset

    def get_unauthenticated_queryset(self, request, search_name, country):
        queryset = HrCompany.objects.all().order_by("-id")

        if bool(search_name):
            queryset = queryset.filter(Q(name__icontains=search_name))

        if bool(country):
            queryset = queryset.filter(Q(countries__id__in=country))

        return queryset

    def get_serializer(self, queryset, request):
        return HrCompanyListSerializer(queryset, many=True, context={"request": request})

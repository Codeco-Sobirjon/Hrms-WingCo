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
    CustomUser,
    JobApply, Favourites, )
from services.pagination_method import (
    Pagination, PaginationFunc
)
from services.renderers import UserRenderers
from apps.authentification.utils.serializers import (
    UserProfilesSerializer, UserDetailSerializers
)
from apps.company.utils.serializers import HrCompanyListSerializer
from apps.enrolls.utils.pagination import StandardResultsSetPagination
from apps.enrolls.utils.serializers import JobApplyListSerilaizer


class UserListView(APIView, PaginationFunc):
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        request=UserProfilesSerializer,
        operation_description="Get users",
    )
    def get(self, request):
        queryset = (
            CustomUser.objects.prefetch_related("groups")
            .filter(groups__name__in=["user"])
            .order_by("-id")
        )
        serializer = super().page(queryset, UserProfilesSerializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    serializers = UserDetailSerializers

    @swagger_auto_schema(
        request=UserProfilesSerializer,
        operation_description="User/Hr/Admin profile",
    )
    def get(self, request, format=None):
        serializer = UserProfilesSerializer(request.user, context={"request": request}) if request.user.is_authenticated else None
        response_data = serializer.data if serializer else {"error": "Token Invalid"}
        status_code = status.HTTP_200_OK if serializer else status.HTTP_404_NOT_FOUND
        return Response(response_data, status=status_code)

    @swagger_auto_schema(
        request=UserDetailSerializers,
        operation_description="User/Hr/Admin update",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="username", type=str),
            OpenApiParameter(name="email", type=str),
            OpenApiParameter(name="first_name", type=str),
            OpenApiParameter(name="last_name", type=str),
            OpenApiParameter(name="bio", type=str),
            OpenApiParameter(name="country", type=str),
            OpenApiParameter(name="city", type=str),
            OpenApiParameter(name="phone", type=str),
            OpenApiParameter(name="avatar", type=str),
        ],
        description="User/Hr/Admin update",
    )
    def put(self, request):
        expected_fields = {"username", "first_name", "last_name", "email", "bio", "country", "city", "phone", "avatar"}
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        if unexpected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        serializers = self.serializers(instance=request.user, data=request.data, partial=True, context={"request": request})

        if not serializers.is_valid():
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)

    def delete(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        request.user.delete()

        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


class DetailsView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializers = UserDetailSerializers

    @swagger_auto_schema(
        request=UserDetailSerializers,
        operation_description="Get user",
    )
    def get(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_object_or_404(CustomUser, id=id)
        serializer = UserProfilesSerializer(queryset,context={"request": request} )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request=UserDetailSerializers,
        operation_description="Update user",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="username", type=str),
            OpenApiParameter(name="email", type=str),
            OpenApiParameter(name="first_name", type=str),
            OpenApiParameter(name="last_name", type=str),
            OpenApiParameter(name="bio", type=str),
            OpenApiParameter(name="country", type=str),
            OpenApiParameter(name="city", type=str),
            OpenApiParameter(name="phone", type=str),
        ],
        description="Update User",
    )
    def put(self, request, id):
        expected_fields = {"username", "first_name", "last_name", "email", "bio", "country", "city", "phone"}
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        if unexpected_fields:
            error_message = f"Unexpected fields in request data: {', '.join(unexpected_fields)}"
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_object_or_404(CustomUser, id=id)
        serializers = self.serializers(instance=queryset, data=request.data, partial=True, context={"request": request})

        if not serializers.is_valid(raise_exception=True):
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response({"error": "Token Invalid"}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_object_or_404(CustomUser, id=id)
        queryset.delete()

        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


class UserStatusView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            count_apply = JobApply.objects.select_related('user').filter(
                user=request.user
            ).count()
            count_rejects = JobApply.objects.select_related('user').filter(
                user=request.user, jobs_status=3
            ).count()
            count_favourites = Favourites.objects.select_related('user').filter(
                user=request.user
            ).count()
            return Response(
                {'count_apply': count_apply, "count_rejects": count_rejects, "count_favourites": count_favourites})
        else:
            return Response({'error': "Token Invalid"})


class PaginationFuncs(Pagination):

    def page(self, instance, serializers, request):
        page = super().paginate_queryset(instance)

        if page is not None:
            serializer = super().get_paginated_response(
                serializers(page, many=True, context={'request': request}).data
            )
        else:
            serializer = serializers(instance, many=True)
        return serializer


class JobApplyUserView(APIView, PaginationFuncs):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user__username"]

    @swagger_auto_schema(
        request=HrCompanyListSerializer,
        operation_description="User applied jobs/ search by username",
    )
    def get(self, request, format=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'error': "Token Invalid"})

        search_name = request.query_params.get("username", None)

        if search_name:
            instance = JobApply.objects.filter(Q(user__username__icontains=search_name))
            serializer = super().page(instance, JobApplyListSerilaizer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        instance = JobApply.objects.select_related("user").filter(user=request.user).order_by("-id")

        serializer = super().page(instance, JobApplyListSerilaizer, request)

        # }

        return Response(serializer.data, status=status.HTTP_200_OK)



from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    JobCategories,
)
from apps.enrolls.utils.serializers import (
    JobCategoriesListSerializer,
    JobCategoriesListsSerializer,
)


class JobCategoriesView(APIView):
    @swagger_auto_schema(
        request=JobCategoriesListSerializer,
        responses={201: JobCategoriesListSerializer(many=True)},
        operation_description="Job categories",
    )
    def get(self, request):
        quryset = JobCategories.objects.all()
        serializer = JobCategoriesListsSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request=JobCategoriesListSerializer,
        responses={201: JobCategoriesListSerializer(many=True)},
        operation_description="Create job categories",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="tag", type=str),
        ],
        description="Create Tag",
    )
    def post(self, request):
        expected_fields = {"tag"}
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        error_message = (
            f"Unexpected fields in request data: "
            f"{', '.join(unexpected_fields)}"
        ) if unexpected_fields else None

        if error_message:
            raise ValidationError({"error": error_message})

        serializer = JobCategoriesListSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class JobCategoriesDetailsView(APIView):
    @swagger_auto_schema(
        request=JobCategoriesListSerializer,
        responses={201: JobCategoriesListSerializer(many=True)},
        operation_description="Job categories",
    )
    def get(self, request, id):
        queryset = get_object_or_404(JobCategories, id=id)
        serializer = JobCategoriesListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request=JobCategoriesListSerializer,
        responses={201: JobCategoriesListSerializer(many=True)},
        operation_description="Job categories update",
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(name="tag", type=str),
        ],
        description="Create Tag",
    )
    def put(self, request, id):
        expected_fields = {"tag"}
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields

        error_message = (
            f"Unexpected fields in request data: "
            f"{', '.join(unexpected_fields)}"
        ) if unexpected_fields else None

        if error_message:
            return Response(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = get_object_or_404(JobCategories, id=id)
        serializers = JobCategoriesListSerializer(
            instance=queryset, data=request.data, partial=True
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(JobCategories, id=id)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)

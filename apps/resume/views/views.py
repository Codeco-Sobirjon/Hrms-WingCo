from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    LevelEducation,
    ResumeUser,
)
from services.renderers import UserRenderers
from apps.resume.utils.serializers import (
    LevelsEducationSerialzier,
    ResumesUserListSerializer,
    ResumeUserCreateSerializer,
)


class LevelEducationView(APIView):
    @swagger_auto_schema(
        request=LevelsEducationSerialzier,
        responses={201: LevelsEducationSerialzier},
        operation_description="Level educations",
    )
    def get(self, request):
        queryset = LevelEducation.objects.all()
        serializer = LevelsEducationSerialzier(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResumeUserDetailsView(APIView):
    render_classes = [UserRenderers]
    permission_class = [IsAuthenticated]

    @swagger_auto_schema(
        request=ResumesUserListSerializer,
        responses={201: ResumesUserListSerializer},
        operation_description="Resume get",
    )
    def get(self, request, id):
        if request.user.is_authenticated:
            queryset = get_object_or_404(ResumeUser, id=id)
            if queryset.user == request.user:
                serializer = ResumesUserListSerializer(queryset, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "You do not have a resume for this ID."})
        else:
            return Response(
                {"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED
            )

    @swagger_auto_schema(
        request=ResumeUserCreateSerializer,
        responses={201: ResumeUserCreateSerializer},
        operation_description="Resume update",
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
    )
    def put(self, request, id):
        if request.user.is_authenticated:
            resume_instance = get_object_or_404(ResumeUser, id=id)
            if resume_instance.user == request.user:
                serializer = ResumeUserCreateSerializer(
                    instance=resume_instance, data=request.data, partial=True
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "You can't update this resume with this ID."})
        else:
            return Response(
                {"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, id):
        if request.user.is_authenticated:
            queryset = get_object_or_404(ResumeUser, id=id)
            if queryset.user == request.user:
                queryset.delete()
                return Response(
                    {"message": "deleted successfully"}, status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "You can't delete this resume with this ID."})
        else:
            return Response(
                {"error": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED
            )

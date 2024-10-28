from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    JobType,
)
from apps.enrolls.utils.serializers import (
    JobTypeSerialzier
)


class JobTypeView(APIView):
    @swagger_auto_schema(
        request=JobTypeSerialzier,
        responses={201: JobTypeSerialzier(many=True)},
        operation_description="Job types",
    )
    def get(self, request):
        queryset = JobType.objects.all()
        serializer = JobTypeSerialzier(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

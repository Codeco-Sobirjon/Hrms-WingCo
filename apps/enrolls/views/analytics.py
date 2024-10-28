import calendar
from datetime import date, timedelta

from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentification.models import (
    JobApply,
    JobCategories,
)


class AnaliticsApplyJobView(APIView):
    @swagger_auto_schema(operation_description="Analytics")
    def get(self, request):
        last_date = calendar.monthrange(date.today().year, date.today().month)[1]

        date_filters = {
            "day": now().date(),
            "week": now().date() - timedelta(days=7),
            "month": now().date() - timedelta(days=last_date),
        }

        result = {}
        for period, date_filter in date_filters.items():
            queryset = (
                JobApply.objects.filter(created_at__gte=date_filter)
                .values(datedate=F("created_at"))
                .annotate(number=Count("id"))
                .order_by("created_at")
            )
            result[period] = queryset

        return Response(result)


class ApllyJobsAnalyticsView(APIView):
    @swagger_auto_schema(operation_description="Analytics filter by id")
    def get(self, request, id):
        filter_categories = get_object_or_404(JobCategories, id=id)
        last_date = calendar.monthrange(date.today().year, date.today().month)[1]

        date_filters = {
            "day": now().date(),
            "week": now().date() - timedelta(days=7),
            "month": now().date() - timedelta(days=last_date),
        }

        result = {}
        for period, date_filter in date_filters.items():
            queryset = (
                JobApply.objects.filter(jobs__job_category=filter_categories)
                .filter(created_at__gte=date_filter)
                .values(datedate=F("created_at"))
                .annotate(number=Count("id"))
                .order_by("created_at")
            )
            result[period] = queryset

        return Response(result, status=status.HTTP_200_OK)

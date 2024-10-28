from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config.views.hr_views import HrListView, HrCompanyAllView
from config.views.remaining_views import (
    CountryCreateViews,
    CountryGetViews,
    NotificationJobsView,
    ResumeFilterView,
    ResumeUserView,
    RolesViews,
    AppliedUsersHrView
)
from config.views.users_views import (
    UserDetailView,
    UserListView,
    UserStatusView,
    DetailsView,
    JobApplyUserView,
)
from config.views.vacancy_views import (
    JobVacanciesDetailsView,
    JobVacanciesView,
    JobVacancyCandidatesView,
    JobVacancyResumeView,
)

admin.site.site_url = None
schema_view = get_schema_view(
    openapi.Info(
        title="HRMS Backend",
        default_version="v1",
        description="HRMS Backend",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="doc.html", extra_context={"schema_url": "api_schema"}
        ),
        name="swagger-ui",
    ),

    path('chat/', include('apps.chat.urls')),
    path('notification/', include('apps.notification.urls')),
    path("auth/", include("apps.authentification.urls")),
    path("vacancy", include("apps.enrolls.urls")),
    path("company", include("apps.company.urls")),
    path("resume/", include("apps.resume.urls")),
    path("roles", RolesViews.as_view()),
    path("users", UserListView.as_view()),
    path("hrs/", HrListView.as_view()),
    path('hr/applied/users', AppliedUsersHrView.as_view()),
    path("user", UserDetailView.as_view()),
    path("user/<int:id>", DetailsView.as_view()),
    path("user/applied-jobs/<int:resumeID>", ResumeFilterView.as_view()),
    path("user/applied-jobs/", JobApplyUserView.as_view()),
    path('user/status', UserStatusView.as_view()),
    # hr companies, search by name search by country
    path("companies/", HrCompanyAllView.as_view()),
    # create country by admin
    path("country", CountryCreateViews.as_view()),
    # get countries
    path("countries", CountryGetViews.as_view()),
    # get vacancies by filter activated is true
    path("vacancies/", JobVacanciesView.as_view()),
    # get vacancies by hr and admin
    path("vacancy/<int:id>", JobVacanciesDetailsView.as_view()),
    # get vacancies candidates
    path("vacancy/<int:id>/candidates/", JobVacancyCandidatesView.as_view()),
    # get vacancies resume
    path("vacancy/<int:id>/resumes/", JobVacancyResumeView.as_view()),
    # resume GET POST
    path("resumes/", ResumeUserView.as_view()),
    # notifications
    path("notifications", NotificationJobsView.as_view()),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]

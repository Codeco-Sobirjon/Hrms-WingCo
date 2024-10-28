from django.urls import path

from apps.company.views.views import (
    CompanyVacancies,
    GetCompaniesView,
    HrCompanyView,
    CompanyReviewCreateView,
    CompanyReviewListView
)

urlpatterns = [
    path("", HrCompanyView.as_view()),
    path("/<int:id>", GetCompaniesView.as_view()),
    path("/<int:id>/review", CompanyReviewCreateView.as_view()),
    path("/<int:id>/reviews", CompanyReviewListView.as_view()),
    path("/<int:id>/vacancies/", CompanyVacancies.as_view()),

]

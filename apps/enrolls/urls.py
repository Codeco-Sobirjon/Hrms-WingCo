from django.urls import path

from apps.enrolls.views.analytics import (
    AnaliticsApplyJobView,
    ApllyJobsAnalyticsView,
)
from apps.enrolls.views.applied import (
    AppllyJobView,
    ApplyJobAcceptOrRejectedView,
    ApplyJobDetailsView,
    JobVacaniesFilterCategories,
)
from apps.enrolls.views.category import (
    JobCategoriesDetailsView,
    JobCategoriesView,
)
from apps.enrolls.views.job_type import (
    JobTypeView
)
from apps.enrolls.views.views import (
    FavouriesListView,
    FavouritesCreateView,
    GetViewerView,
    NotificationSeenJobsView,
)

urlpatterns = [
    # job types
    path("/types", JobTypeView.as_view()),
    # job categories
    path("/categories", JobCategoriesView.as_view()),
    path("/categories/<int:id>", JobCategoriesDetailsView.as_view()),
    # job vacancies
    path("/viewers/<int:id>", GetViewerView.as_view()),
    # job apply
    path("/applied-create", AppllyJobView.as_view()),
    path("/<int:id>/<int:status_id>", ApplyJobAcceptOrRejectedView.as_view()),
    path("/applied-job/<int:id>", ApplyJobDetailsView.as_view()),
    # filter by status (accepted / rejected)
    path("/applied/filter/", JobVacaniesFilterCategories.as_view()),
    # notification
    path("/notification-seen/<int:id>", NotificationSeenJobsView.as_view()),
    # analytics
    path("/analytics", AnaliticsApplyJobView.as_view()),
    path("/analytics/<int:id>", ApllyJobsAnalyticsView.as_view()),
    # favorites
    path("/favorites", FavouriesListView.as_view()),
    path("/<int:id>/favorite", FavouritesCreateView.as_view()),
]

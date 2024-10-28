from django.urls import path

from apps.resume.views.views import (
    ResumeUserDetailsView,
    LevelEducationView,

)

urlpatterns = [
    path('<int:id>', ResumeUserDetailsView.as_view()),
    path('level-education-list', LevelEducationView.as_view()),
]

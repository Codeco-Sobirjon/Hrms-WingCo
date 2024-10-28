from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin

from apps.authentification.models import (
    LevelEducation,
    ResumeUser,
    HrCompany,
    Favourites,
    Countries,
    SmsHistory,
    JobCategories,
    JobVacancies,
    JobApply,
    StatusApply,
    NotificationJobs,
    JobType,
    CompanyReview,
    CustomUser
)


class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_active', 'is_staff']
    search_fields = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Personal Information', {'fields': ('phone', 'country', 'city', 'bio', 'avatar',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


class LevelEducationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'level']


class ResumeUserHrCompanyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'user', 'job_tag']


class HrCompanyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name']


class CountriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name']


class JobCategoriesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'tag']


class JobVacanciesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'title']


class StatusApplyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name']


class JobApplyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'user', 'jobs']


class CompanyReviewsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'user', 'company', 'comment']


class FavouritesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'user', 'jobs', 'created_at']


class NotificationJobsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'job_apply', 'jobs_status', 'is_seen', 'user']


class JobTypeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'type']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SmsHistory)
admin.site.register(CompanyReview, CompanyReviewsAdmin)
admin.site.register(HrCompany, HrCompanyAdmin)
admin.site.register(Countries, CountriesAdmin)
admin.site.register(Favourites, FavouritesAdmin)
admin.site.register(ResumeUser, ResumeUserHrCompanyAdmin)
admin.site.register(LevelEducation, LevelEducationAdmin)
admin.site.register(JobCategories, JobCategoriesAdmin)
admin.site.register(JobVacancies, JobVacanciesAdmin)
admin.site.register(JobApply, JobApplyAdmin)
admin.site.register(StatusApply, StatusApplyAdmin)
admin.site.register(NotificationJobs, NotificationJobsAdmin)
admin.site.register(JobType, JobTypeAdmin)

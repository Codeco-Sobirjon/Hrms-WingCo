from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "table_user"
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"


class SmsHistory(models.Model):
    code = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="smscode",
    )

    class Meta:
        db_table = "table_sms_history"
        verbose_name = "History User code"
        verbose_name_plural = "History User codes"


class Countries(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "table_countries"
        verbose_name = "Countries"
        verbose_name_plural = "Countries"


class HrCompany(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    logo = models.ImageField(upload_to="logo/", null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    users = models.ManyToManyField(
        CustomUser, null=True, blank=True, related_name="companyuser"
    )
    created_at = models.DateField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="author",
    )
    countries = models.ManyToManyField(
        Countries, null=True, blank=True, related_name="countrycompany"
    )
    hrs = models.ManyToManyField(
        CustomUser, null=True, blank=True, related_name="hrsusers"
    )
    sub_company = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcompany",
    )

    class Meta:
        db_table = "table_companies"
        verbose_name = "Company"
        verbose_name_plural = "Companies"


class CompanyReview(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    company = models.ForeignKey(
        HrCompany, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "table_company_review"
        verbose_name = "Company Review"
        verbose_name_plural = "Company Review"


class LevelEducation(models.Model):
    level = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "table_level_education"
        verbose_name = "Level Education"
        verbose_name_plural = "Level Education"


class JobCategories(models.Model):
    tag = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "table_job_categories"
        verbose_name = "Job Category"
        verbose_name_plural = "Job Categories"


class ResumeUser(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    job_tag = models.ForeignKey(
        JobCategories, on_delete=models.CASCADE, null=True, blank=True
    )
    content = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    date_of_brith = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    level_of_education = models.ForeignKey(
        LevelEducation, on_delete=models.CASCADE, null=True, blank=True
    )
    place_of_study = models.JSONField(null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    job_experiences = models.JSONField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = "table_resumes"
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"


class JobType(models.Model):
    type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "table_job_type"
        verbose_name = "Job Type"
        verbose_name_plural = "Job Types"


class JobVacancies(models.Model):
    job_category = models.ForeignKey(
        JobCategories,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categor_id",
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    salary = models.FloatField(default=0, null=True, blank=True)
    qualifications = models.CharField(max_length=255, null=True, blank=True)
    job_type = models.ForeignKey(
        JobType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="job_type",
    )
    company = models.ForeignKey(
        HrCompany, on_delete=models.CASCADE, null=True, blank=True
    )
    experience = models.BooleanField(default=False, null=True, blank=True)
    skills = models.JSONField(null=True, blank=True)
    level = models.IntegerField(default=0, null=True, blank=True)
    work_hours = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)
    is_seen = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)
    is_look_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, null=True, blank=True, related_name="isLookUser"
    )
    is_activate = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = "table_vacancy"
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"


class Favourites(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favourites",
    )
    jobs = models.ForeignKey(
        JobVacancies,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vacancies",
    )
    # isFavorite = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "table_favourites"
        verbose_name = "Favourites"
        verbose_name_plural = "Favourites"


class StatusApply(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "table_status_apply"
        verbose_name = "Status Apply"
        verbose_name_plural = "Status Apply"


class JobApply(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    jobs = models.ForeignKey(
        JobVacancies,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="jobs",
    )
    jobs_status = models.ForeignKey(
        StatusApply, on_delete=models.CASCADE, null=True, blank=True, default=1
    )
    resume = models.ForeignKey(
        ResumeUser, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateField(
        auto_now_add=True,
        auto_now=False,
    )

    class Meta:
        db_table = "table_job_apply"
        verbose_name = "Job Apply"
        verbose_name_plural = "Job Apply"


class NotificationJobs(models.Model):
    job_apply = models.ForeignKey(
        JobApply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    jobs_status = models.ForeignKey(
        StatusApply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_seen = models.BooleanField(default=False, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notificationjob",
    )
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)


    class Meta:
        db_table = "table_job_notification"
        verbose_name = "Job Notification"
        verbose_name_plural = "Job Notification"



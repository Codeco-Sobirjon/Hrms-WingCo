from django.db import models
from django.conf import settings

NOTIFICATION_TYPES = (
    ('MESSAGE_SENT', 'MESSAGE_SENT'),
    ('MESSAGE_ACCEPT', 'MESSAGE_ACCEPT'),
)


class Notification(models.Model):
    name = models.CharField(max_length=32, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender_notification')
    message = models.CharField(max_length=255, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "table_notification"
        verbose_name = "Notification"
        verbose_name_plural = "Notification"
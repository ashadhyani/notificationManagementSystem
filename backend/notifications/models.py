from django.db import models
from django.contrib.auth.models import User

class Trigger(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('web_push', 'Web Push'),
    ]

    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE, related_name='templates')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    is_enabled = models.BooleanField(default=True)
    subject = models.CharField(max_length=255, blank=True, default='')
    body = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('trigger', 'channel')

    def __str__(self):
        return f"{self.trigger.name} - {self.get_channel_display()} ({'ON' if self.is_enabled else 'OFF'})"

class WebPushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='web_push_subscriptions')
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription {self.id} for {self.user.username if self.user else 'Guest'}"

class NotificationLog(models.Model):
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    trigger_code = models.CharField(max_length=50)
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}] {self.trigger_code} -> {self.channel} ({self.recipient}) at {self.sent_at}"

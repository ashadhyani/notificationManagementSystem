from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trigger, NotificationTemplate, NotificationLog, WebPushSubscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class NotificationTemplateSerializer(serializers.ModelSerializer):
    trigger_code = serializers.CharField(source='trigger.code', read_only=True)
    trigger_name = serializers.CharField(source='trigger.name', read_only=True)

    class Meta:
        model = NotificationTemplate
        fields = ['id', 'trigger', 'trigger_code', 'trigger_name', 'channel', 'is_enabled', 'subject', 'body', 'updated_at']
        read_only_fields = ['id', 'trigger', 'trigger_code', 'trigger_name', 'channel', 'updated_at']

class TriggerSerializer(serializers.ModelSerializer):
    templates = NotificationTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = Trigger
        fields = ['id', 'code', 'name', 'description', 'templates']

class WebPushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebPushSubscription
        fields = ['id', 'endpoint', 'p256dh', 'auth', 'created_at']

class NotificationLogSerializer(serializers.ModelSerializer):
    sent_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = ['id', 'trigger_code', 'channel', 'recipient', 'status', 'error_message', 'sent_at_formatted']

    def get_sent_at_formatted(self, obj):
        from django.utils import timezone
        if not obj.sent_at:
            return ""
        local_dt = timezone.localtime(obj.sent_at)
        return local_dt.strftime("%Y-%m-%d %I:%M:%S %p")

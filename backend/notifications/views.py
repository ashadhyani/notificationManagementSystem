import logging
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)

from .models import Trigger, NotificationTemplate, NotificationLog, WebPushSubscription
from .serializers import (
    TriggerSerializer,
    NotificationTemplateSerializer,
    NotificationLogSerializer,
    UserSerializer,
)
from .services.dispatcher import dispatch_notifications, send_single_test_notification

# ==============================================================================
# Authentication & Trigger Views (Real Login/Logout actions fire triggers)
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registers a new user."""
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()
    is_admin = request.data.get('is_admin', False)

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_staff=is_admin,
        is_superuser=is_admin,
    )
    return Response({
        'message': 'User registered successfully.',
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticates user and SYNCHRONOUSLY fires the 'login' trigger.
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)

    # Synchronously dispatch notifications for 'login' trigger
    phone = request.data.get('phone')
    dispatch_results = []
    try:
        dispatch_results = dispatch_notifications(
            trigger_code='login',
            user=user,
            recipient_email=user.email,
            recipient_phone=phone,
        )
    except Exception as exc:
        logger.exception("Error during login notification dispatch: %s", exc)

    return Response({
        'message': f"Welcome back, {user.username}! Login trigger executed.",
        'user': UserSerializer(user).data,
        'trigger_fired': 'login',
        'notifications_dispatched': dispatch_results,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logs out user and SYNCHRONOUSLY fires the 'logout' trigger.
    """
    user = request.user if request.user.is_authenticated else None
    user_data = UserSerializer(user).data if user else None

    # Synchronously dispatch notifications for 'logout' trigger
    dispatch_results = []
    try:
        dispatch_results = dispatch_notifications(
            trigger_code='logout',
            user=user,
            recipient_email=user.email if user else None,
        )
    except Exception as exc:
        logger.exception("Error during logout notification dispatch: %s", exc)

    if request.user.is_authenticated:
        logout(request)

    return Response({
        'message': 'Logged out successfully. Logout trigger executed.',
        'user': user_data,
        'trigger_fired': 'logout',
        'notifications_dispatched': dispatch_results,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user_view(request):
    """Returns current user status and whether user is an admin."""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data,
        })
    return Response({
        'authenticated': False,
        'user': None,
    })


# ==============================================================================
# Admin 2x3 Matrix & Template Management Views
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def matrix_view(request):
    """
    Returns the 2x3 matrix data:
    Rows = Triggers (Login, Logout)
    Cols = Channels (WhatsApp, Email, Web Push)
    """
    triggers = Trigger.objects.prefetch_related('templates').order_by('id')
    serializer = TriggerSerializer(triggers, many=True)
    return Response({
        'channels': ['whatsapp', 'email', 'web_push'],
        'triggers': serializer.data,
    })


@api_view(['PATCH'])
@permission_classes([AllowAny])
def toggle_template_view(request, template_id):
    """Toggles a template cell ON or OFF."""
    template = get_object_or_404(NotificationTemplate, id=template_id)
    template.is_enabled = not template.is_enabled
    template.save()
    return Response({
        'message': f"{template.trigger.name} - {template.get_channel_display()} is now {'ON' if template.is_enabled else 'OFF'}.",
        'template': NotificationTemplateSerializer(template).data,
    })


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_template_view(request, template_id):
    """Updates a template's subject and body."""
    template = get_object_or_404(NotificationTemplate, id=template_id)
    subject = request.data.get('subject', template.subject)
    body = request.data.get('body', template.body)

    template.subject = subject
    template.body = body
    template.save()

    return Response({
        'message': 'Template updated successfully.',
        'template': NotificationTemplateSerializer(template).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def test_send_template_view(request, template_id):
    """Sends an immediate test notification for a specific cell."""
    template = get_object_or_404(NotificationTemplate, id=template_id)
    recipient = request.data.get('recipient')

    success, message = send_single_test_notification(template, test_recipient=recipient)
    return Response({
        'success': success,
        'channel': template.channel,
        'trigger': template.trigger.name,
        'message': message,
    }, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# Web Push Views (VAPID Key & Subscription)
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def vapid_public_key_view(request):
    """Returns VAPID Public Key for browser Web Push registration."""
    key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
    return Response({'vapid_public_key': key})


@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_web_push_view(request):
    """Stores browser PushManager subscription."""
    endpoint = request.data.get('endpoint')
    keys = request.data.get('keys', {})
    p256dh = keys.get('p256dh', '')
    auth = keys.get('auth', '')

    if not endpoint or not p256dh or not auth:
        return Response({'error': 'Invalid subscription payload.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user if request.user.is_authenticated else None

    # Update existing or create new
    sub, _ = WebPushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'user': user,
            'p256dh': p256dh,
            'auth': auth,
        }
    )
    return Response({'message': 'Web Push subscription registered successfully.', 'id': sub.id})


# ==============================================================================
# Notification Logs
# ==============================================================================

@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def notification_logs_view(request):
    """Returns recent notification delivery logs or clears all logs."""
    if request.method == 'DELETE':
        deleted_count, _ = NotificationLog.objects.all().delete()
        return Response({'status': 'success', 'message': f'Cleared {deleted_count} logs.'})

    logs = NotificationLog.objects.order_by('-sent_at')[:50]
    serializer = NotificationLogSerializer(logs, many=True)
    return Response(serializer.data)

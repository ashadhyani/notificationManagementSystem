import datetime
import logging
from django.utils import timezone
from ..models import Trigger, NotificationTemplate, NotificationLog, WebPushSubscription
from .whatsapp import send_whatsapp_message
from .email_service import send_transactional_email
from .webpush_service import send_web_push_notification

logger = logging.getLogger(__name__)

def render_template_string(template_str: str, context: dict) -> str:
    """Replaces {{variable}} placeholders with real context data."""
    if not template_str:
        return ''
    rendered = template_str
    for key, val in context.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(val if val is not None else ''))
    return rendered

def dispatch_notifications(trigger_code: str, user=None, recipient_email: str = None, recipient_phone: str = None) -> list:
    """
    Synchronously dispatches notifications across all enabled channels for the specified trigger ('login' or 'logout').
    Never crashes the caller if a channel fails.
    """
    trigger = Trigger.objects.filter(code=trigger_code).first()
    if not trigger:
        logger.warning("Trigger '%s' not found in database.", trigger_code)
        return []

    # Prepare context dictionary for dynamic variables
    user_name = user.username if user else 'Guest'
    fallback_email = getattr(settings, 'EMAIL_TEST_RECIPIENT', '').strip()
    if recipient_email and recipient_email not in ('admin@notifications.com', 'user@example.com'):
        email = recipient_email
    elif user and user.email and user.email not in ('admin@notifications.com', 'user@example.com'):
        email = user.email
    elif fallback_email:
        email = fallback_email
    else:
        email = recipient_email or (user.email if user and user.email else 'admin@notifications.com')

    fallback_phone = getattr(settings, 'WHATSAPP_TEST_RECIPIENT', '').strip()
    phone = recipient_phone or getattr(user, 'phone_number', None) or fallback_phone or ''
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    context = {
        'user_name': user_name,
        'email': email,
        'phone': phone,
        'time': current_time,
        'trigger': trigger.name,
    }

    # Fetch enabled templates for this trigger
    enabled_templates = NotificationTemplate.objects.filter(trigger=trigger, is_enabled=True)
    results = []

    for template in enabled_templates:
        channel = template.channel
        subject = render_template_string(template.subject, context)
        body = render_template_string(template.body, context)

        success = False
        message = ""
        target_recipient = ""

        try:
            if channel == 'whatsapp':
                target_recipient = phone or 'Default Sandbox Phone'
                success, message = send_whatsapp_message(to_number=phone, message_body=body)

            elif channel == 'email':
                target_recipient = email
                success, message = send_transactional_email(to_email=email, subject=subject, body=body)

            elif channel == 'web_push':
                # Query registered subscriptions for this user, or any active subscription
                subscriptions = WebPushSubscription.objects.all()
                if user and user.is_authenticated:
                    user_subs = subscriptions.filter(user=user)
                    if user_subs.exists():
                        subscriptions = user_subs

                if subscriptions.exists():
                    sub = subscriptions.first()
                    target_recipient = f"Browser Endpoint ({sub.endpoint[:30]}...)"
                    sub_info = {
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth,
                        }
                    }
                    success, message = send_web_push_notification(sub_info, title=subject or trigger.name, body=body)
                else:
                    target_recipient = "Browser (No Active Subscription)"
                    success, message = send_web_push_notification(None, title=subject or trigger.name, body=body)

        except Exception as ex:
            success = False
            message = f"Dispatch Error: {str(ex)}"
            logger.exception("Error in synchronous dispatcher for channel %s", channel)

        # Log entry in NotificationLog
        log = NotificationLog.objects.create(
            trigger_code=trigger_code,
            channel=channel,
            recipient=target_recipient or 'N/A',
            status='SENT' if success else 'FAILED',
            error_message='' if success else message
        )

        results.append({
            'channel': channel,
            'status': 'SENT' if success else 'FAILED',
            'recipient': target_recipient,
            'message': message,
            'log_id': log.id,
        })

    return results

def send_single_test_notification(template: NotificationTemplate, test_recipient: str = None) -> tuple[bool, str]:
    """
    Sends an immediate test notification for a specific matrix cell.
    """
    channel = template.channel
    trigger = template.trigger

    context = {
        'user_name': 'TestAdmin',
        'email': test_recipient or 'admin@notifications.com',
        'phone': test_recipient or '',
        'time': timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        'trigger': f"{trigger.name} (Test Send)",
    }

    subject = render_template_string(template.subject, context) or f"Test: {trigger.name}"
    body = render_template_string(template.body, context) or f"This is a test notification for {trigger.name} on {channel}."

    success = False
    message = ""
    target_recipient = test_recipient or "Default Recipient"

    try:
        if channel == 'whatsapp':
            success, message = send_whatsapp_message(to_number=test_recipient, message_body=body)
        elif channel == 'email':
            fallback_mail = getattr(settings, 'EMAIL_TEST_RECIPIENT', '').strip()
            recipient = test_recipient or fallback_mail or 'admin@notifications.com'
            target_recipient = recipient
            success, message = send_transactional_email(to_email=recipient, subject=subject, body=body)
        elif channel == 'web_push':
            # Use most recent subscription if available
            sub = WebPushSubscription.objects.last()
            if sub:
                target_recipient = f"Browser Endpoint ({sub.endpoint[:30]}...)"
                sub_info = {
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    }
                }
                success, message = send_web_push_notification(sub_info, title=subject, body=body)
            else:
                target_recipient = "Browser (No Active Subscription)"
                success, message = send_web_push_notification(None, title=subject, body=body)
    except Exception as ex:
        success = False
        message = str(ex)

    NotificationLog.objects.create(
        trigger_code=f"{trigger.code}_test",
        channel=channel,
        recipient=target_recipient,
        status='SENT' if success else 'FAILED',
        error_message='' if success else message
    )

    return success, message

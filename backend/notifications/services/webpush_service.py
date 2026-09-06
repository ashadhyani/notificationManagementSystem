import json
import logging
from django.conf import settings
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

def send_web_push_notification(subscription_info: dict, title: str, body: str) -> tuple[bool, str]:
    """
    Sends real Web Push notification using pywebpush and VAPID keys to browser push servers.
    subscription_info format:
    {
        "endpoint": "https://fcm.googleapis.com/fcm/send/...",
        "keys": {
            "p256dh": "...",
            "auth": "..."
        }
    }
    """
    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    vapid_claims = {
        "sub": f"mailto:{getattr(settings, 'VAPID_ADMIN_EMAIL', 'admin@notifications.com')}"
    }

    payload = json.dumps({
        "title": title or "Notification",
        "body": body,
        "icon": "/static/favicon.ico",
        "badge": "/static/favicon.ico",
    })

    if not subscription_info or not subscription_info.get("endpoint"):
        logger.info("[Web Push Simulation] No active browser subscription. Title: %s, Body: %s", title, body)
        return True, "Simulated Web Push (No browser subscription endpoint registered yet)."

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
            timeout=10
        )
        return True, f"Delivered to browser endpoint: {subscription_info['endpoint'][:40]}..."
    except WebPushException as ex:
        err = f"WebPushException: {str(ex)}"
        logger.error(err)
        return False, err
    except Exception as e:
        logger.exception("Web Push delivery error")
        return False, str(e)

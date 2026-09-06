import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_transactional_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    """
    Sends transactional email using Resend or Postmark API based on EMAIL_PROVIDER setting.
    """
    provider = getattr(settings, 'EMAIL_PROVIDER', 'resend').lower()
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'onboarding@resend.dev').strip()
    api_key = getattr(settings, 'EMAIL_API_KEY', '').strip()
    postmark_token = getattr(settings, 'POSTMARKAPP_TOKEN', '').strip()

    recipient = to_email.strip() if to_email else ''
    if not recipient or recipient.endswith('@notifications.com') or recipient.endswith('@example.com'):
        recipient = (getattr(settings, 'EMAIL_TEST_RECIPIENT', '') or 'asha3451@hotmail.com').strip()

    # 1. Postmark Provider
    if provider == 'postmark':
        token = postmark_token or api_key
        if not token or not recipient:
            logger.info("[Postmark Sandbox Simulation] Email to %s | Subject: %s", recipient or 'N/A', subject)
            return True, f"Simulated delivery (Postmark token not configured in .env). Recipient: {recipient or 'N/A'}"

        url = "https://api.postmarkapp.com/email"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Postmark-Server-Token": token,
        }
        payload = {
            "From": from_email,
            "To": recipient,
            "Subject": subject or "Notification",
            "TextBody": body,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                return True, f"Delivered via Postmark. MessageID: {resp.json().get('MessageID')}"
            else:
                err = f"Postmark Error {resp.status_code}: {resp.text}"
                logger.error(err)
                return False, err
        except Exception as e:
            logger.exception("Postmark send error")
            return False, str(e)

    # 2. Resend Provider (Default)
    else:
        if not api_key or not recipient:
            logger.info("[Resend Sandbox Simulation] Email to %s | Subject: %s", recipient or 'N/A', subject)
            return True, f"Simulated delivery (Resend API key not configured in .env). Recipient: {recipient or 'N/A'}"

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": from_email,
            "to": [recipient],
            "subject": subject or "Notification",
            "text": body,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                return True, f"Delivered via Resend. Email ID: {resp.json().get('id')}"
            else:
                err = f"Resend Error {resp.status_code}: {resp.text}"
                logger.error(err)
                return False, err
        except Exception as e:
            logger.exception("Resend send error")
            return False, str(e)

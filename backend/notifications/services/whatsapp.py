import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_whatsapp_message(to_number: str, message_body: str) -> tuple[bool, str]:
    """
    Sends a WhatsApp message via Meta WhatsApp Cloud API Sandbox.
    API Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/
    """
    access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '').strip()
    phone_number_id = getattr(settings, 'PHONE_NUMBER_ID', '').strip()
    recipient = to_number.strip() if to_number else getattr(settings, 'WHATSAPP_TEST_RECIPIENT', '').strip()

    # Fallback to simulated delivery if credentials are not configured
    if not access_token or not phone_number_id or not recipient:
        logger.info("[WhatsApp Sandbox Simulation] Message to %s: %s", recipient or 'Sandbox Default', message_body)
        return True, f"Simulated delivery (Meta WhatsApp Cloud API credentials not configured in .env). Recipient: {recipient or 'N/A'}"

    # Clean phone number (strip '+' or whitespace)
    clean_phone = recipient.replace('+', '').replace(' ', '').replace('-', '')
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_body,
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            return True, f"Delivered via WhatsApp Cloud API: {response.json().get('messages', [{}])[0].get('id', 'OK')}"
        else:
            err = f"WhatsApp API Error {response.status_code}: {response.text}"
            logger.error(err)
            return False, err
    except Exception as e:
        logger.exception("Failed to dispatch WhatsApp message")
        return False, str(e)

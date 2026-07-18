"""
SMS Sender via Simple SMS Gateway App
======================================

Sends SMS through the "Simple SMS Gateway" Android app
running on the same Wi-Fi network.

The app runs a local HTTP server on the phone.
We send POST requests to: http://<phone-ip>:8080/send-sms

No USB cable, no root, no ADB needed!

Requirements:
- "Simple SMS Gateway" app installed on Android phone
- App server must be running (green "Running" status)
- Phone and PC must be on the same Wi-Fi network
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Get gateway URL from Django settings
GATEWAY_URL = getattr(settings, 'SMS_GATEWAY_URL', 'http://192.168.31.238:8080')
SEND_SMS_ENDPOINT = f"{GATEWAY_URL}/send-sms"
TIMEOUT = 15  # seconds


def send_sms(phone_number, message):
    """
    Send SMS through the Simple SMS Gateway app.

    Args:
        phone_number: Receiver's phone number
        message: SMS text message

    Returns:
        (success: bool, error_message: str)
    """
    try:
        # Clean the phone number
        phone_number = phone_number.replace(" ", "").strip()

        # Send POST request to the gateway app
        payload = {
            "phone": phone_number,
            "message": message
        }

        response = requests.post(
            SEND_SMS_ENDPOINT,
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            logger.info(f"SMS sent successfully to {phone_number}")
            return True, ""
        else:
            error = f"Gateway returned status {response.status_code}: {response.text}"
            logger.error(error)
            return False, error

    except requests.ConnectionError:
        error = "Cannot connect to SMS Gateway app. Make sure the app is running on your phone and both devices are on the same Wi-Fi."
        logger.error(error)
        return False, error
    except requests.Timeout:
        error = "Connection to SMS Gateway app timed out."
        logger.error(error)
        return False, error
    except Exception as e:
        error = f"Error sending SMS: {str(e)}"
        logger.error(error)
        return False, error


def is_gateway_available():
    """Check if the SMS Gateway app is reachable."""
    try:
        # Try to connect to the gateway server
        response = requests.get(GATEWAY_URL, timeout=5)
        return True
    except Exception:
        return False


def check_status():
    """
    Check SMS Gateway app status.
    Returns a dict with status info for the web UI.
    """
    status = {
        "adb_installed": True,  # Not using ADB anymore, but keep key for UI compatibility
        "device_connected": False,
        "device_info": None,
        "ready": False,
        "message": "",
        "gateway_type": "wifi"
    }

    try:
        response = requests.get(GATEWAY_URL, timeout=5)
        status["device_connected"] = True
        status["ready"] = True
        status["device_info"] = {
            "model": "Wi-Fi Gateway",
            "android_version": "SMS App"
        }
        status["message"] = "Connected: SMS Gateway App (Wi-Fi)"
        return status

    except requests.ConnectionError:
        status["message"] = "SMS Gateway app not reachable. Make sure the app is running on your phone."
        return status
    except requests.Timeout:
        status["message"] = "SMS Gateway app connection timed out."
        return status
    except Exception as e:
        status["message"] = f"Error checking gateway: {str(e)}"
        return status

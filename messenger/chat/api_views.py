from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import SMS
from .serializers import SMSSerializer
from . import sms_sender


def check_api_key(request):
    """Validate API key from request header."""
    api_key = request.headers.get("X-API-Key", "")
    expected_key = getattr(settings, "SMS_GATEWAY_API_KEY", "")
    if not expected_key or api_key != expected_key:
        return False
    return True


@api_view(["GET"])
def pending_sms(request):
    """Get all pending SMS messages for the gateway to send."""
    if not check_api_key(request):
        return Response({"error": "Invalid API Key"}, status=403)

    sms_list = SMS.objects.filter(status="Pending")
    serializer = SMSSerializer(sms_list, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def update_status(request):
    """Update SMS status after gateway sends/fails."""
    if not check_api_key(request):
        return Response({"error": "Invalid API Key"}, status=403)

    sms_id = request.data.get("id")
    status = request.data.get("status")
    error_message = request.data.get("error_message", "")

    if status not in ["Sent", "Failed", "Sending"]:
        return Response({
            "success": False,
            "message": "Invalid status. Must be Sent, Failed, or Sending."
        }, status=400)

    try:
        sms = SMS.objects.get(id=sms_id)
        sms.status = status
        sms.attempts += 1

        if status == "Sent":
            sms.sent_at = timezone.now()
        elif status == "Failed":
            sms.error_message = error_message

        sms.save()

        return Response({
            "success": True,
            "message": f"Status updated to {status}"
        })

    except SMS.DoesNotExist:
        return Response({
            "success": False,
            "message": "SMS Not Found"
        }, status=404)


@api_view(["GET"])
def sms_history(request):
    """Get recent SMS history for the web UI."""
    sms_list = SMS.objects.all()[:50]
    serializer = SMSSerializer(sms_list, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def adb_status(request):
    """Get connected USB device/ADB status."""
    status = sms_sender.check_status()
    return Response(status)


@api_view(["POST"])
def clear_history(request):
    """Clear all message history from the database."""
    try:
        SMS.objects.all().delete()
        return Response({"success": True, "message": "Message history cleared successfully!"})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)
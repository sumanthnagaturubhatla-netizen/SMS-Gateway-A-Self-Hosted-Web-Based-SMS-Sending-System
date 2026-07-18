from django.shortcuts import render
from django.http import JsonResponse
from .models import SMS
from . import sms_sender


def home(request):
    """Main page - SMS compose form + history."""

    if request.method == "POST":
        sender = request.POST.get("sender_number", "").strip()
        receiver = request.POST.get("receiver_number", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([sender, receiver, message]):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "error": "All fields are required."},
                    status=400
                )
            return render(request, "chat/index.html", {
                "error": "All fields are required."
            })

        # Create record in DB as Sending
        sms = SMS.objects.create(
            sender_number=sender,
            receiver_number=receiver,
            message=message,
            status="Sending"
        )

        # Attempt to send immediately via USB-connected ADB Android phone
        success, error_msg = sms_sender.send_sms(receiver, message)

        if success:
            sms.status = "Sent"
            sms.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "message": "SMS sent successfully via USB-connected phone!",
                    "sms_id": sms.id
                })
        else:
            sms.status = "Failed"
            sms.error_message = error_msg
            sms.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False,
                    "error": f"Failed to send: {error_msg}",
                    "sms_id": sms.id
                }, status=500)

    # Check connection status to show on the UI
    adb_status = sms_sender.check_status()

    return render(request, "chat/index.html", {"adb_status": adb_status})
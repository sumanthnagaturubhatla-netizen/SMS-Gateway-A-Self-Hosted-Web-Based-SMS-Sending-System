from django.contrib import admin
from .models import SMS


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    list_display = (
        "sender_number",
        "receiver_number",
        "status",
        "created_at",
        "sent_at",
    )

    list_filter = ("status",)

    search_fields = (
        "sender_number",
        "receiver_number",
    )
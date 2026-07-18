from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path("", views.home, name="home"),

    # API endpoints for the Android gateway (backward compatibility)
    path(
        "api/pending-sms/",
        api_views.pending_sms,
        name="pending_sms"
    ),
    path(
        "api/update-status/",
        api_views.update_status,
        name="update_status"
    ),

    # API endpoints for web UI
    path(
        "api/sms-history/",
        api_views.sms_history,
        name="sms_history"
    ),
    path(
        "api/adb-status/",
        api_views.adb_status,
        name="adb_status"
    ),
    path(
        "api/clear-history/",
        api_views.clear_history,
        name="clear_history"
    ),
]
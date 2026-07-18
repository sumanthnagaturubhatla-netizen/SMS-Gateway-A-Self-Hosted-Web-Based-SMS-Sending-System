from django.db import models


class SMS(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Sending", "Sending"),
        ("Sent", "Sent"),
        ("Failed", "Failed"),
    ]

    sender_number = models.CharField(max_length=15)
    receiver_number = models.CharField(max_length=15)
    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    error_message = models.TextField(blank=True, default="")
    attempts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.receiver_number} ({self.status})"
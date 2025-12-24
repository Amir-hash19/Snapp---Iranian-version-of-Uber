from account.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Order(models.Model):

    PENDING = "pending"
    ACCEPTED = "accepted"
    STARTED = "started"
    FINISHED = "finished"
    CANCELED = "canceled"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (STARTED, "Started"),
        (FINISHED, "Finished"),
        (CANCELED, "Canceled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    driver = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_orders",
    )

    origin_lat = models.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)

    distance_meters = models.PositiveIntegerField()
    duration_seconds = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING, db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

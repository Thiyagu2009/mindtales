from datetime import datetime, timezone
import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint

from restaurant.models import Menu

User = get_user_model()


class Vote(models.Model):
    RANK_CHOICES = [
        (1, "1st (3 points)"),
        (2, "2nd (2 points)"),
        (3, "3rd (1 point)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="votes")
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="votes")
    rank = models.IntegerField(
        choices=RANK_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    created_at = models.DateTimeField(default=datetime.now)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "menu"],
                condition=models.Q(
                    created_at__date=models.F("created_at__date")),
                name="unique_user_menu_per_day",
            )
        ]

    @property
    def points(self):
        return 4 - self.rank

    def save(self, *args, **kwargs):
        if self.menu.date != datetime.now(timezone.utc).date():
            raise ValueError("Can only vote for today's menus.")
        super().save(*args, **kwargs)

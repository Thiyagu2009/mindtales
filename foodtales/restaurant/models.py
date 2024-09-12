import uuid
from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="menus"
    )
    date = models.DateField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["restaurant", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.restaurant.restaurant_name} - Menu for {self.date}"


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ("appetizer", "Appetizer"),
        ("main_course", "Main Course"),
        ("dessert", "Dessert"),
        ("beverage", "Beverage"),
    ]

    menu = models.ForeignKey(Menu, related_name="items", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.menu.restaurant.restaurant_name}"

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ("restaurant", "Restaurant"),
        ("employee", "Employee"),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    # Fields for Restaurant
    restaurant_name = models.CharField(max_length=100, blank=True, null=True)
    restaurant_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    # Fields for Employee
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the ID if it's a new object
            if self.user_type == "restaurant" and not self.restaurant_id:
                self.restaurant_id = self.generate_unique_id("R")
            elif self.user_type == "employee" and not self.employee_id:
                self.employee_id = self.generate_unique_id("E")
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_id(prefix):
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id"],
                condition=models.Q(user_type="employee"),
                name="unique_employee_id",
            ),
            models.UniqueConstraint(
                fields=["restaurant_id"],
                condition=models.Q(user_type="restaurant"),
                name="unique_restaurant_id",
            ),
        ]

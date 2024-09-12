from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RestaurantSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password", "restaurant_name")
        read_only_fields = ("restaurant_id",)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("The two password fields didn't match.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            user_type="restaurant",
            restaurant_name=validated_data["restaurant_name"],
        )
        return user

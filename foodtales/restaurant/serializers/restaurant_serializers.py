from rest_framework import serializers
from django.contrib.auth import get_user_model

from restaurant.models import Menu
from restaurant.serializers.menu_items_serializers import MenuItemSerializer

User = get_user_model()


class RestaurantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "restaurant_name", "restaurant_id"]


class MenuWithRestaurantSerializer(serializers.ModelSerializer):
    restaurant = RestaurantDetailSerializer(read_only=True)
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ["id", "date", "is_published", "restaurant", "items"]


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "restaurant_name", "restaurant_id"]


class MenuWithVotesSerializer(serializers.ModelSerializer):
    total_points = serializers.IntegerField(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ["id", "date", "is_published", "restaurant", "total_points",
                  "items"]

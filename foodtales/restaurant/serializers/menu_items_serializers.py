from django.utils import timezone
from rest_framework import serializers

from restaurant.models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "description", "price", "category",
                  "is_available"]


class MenuSerializer(serializers.ModelSerializer):
    date = serializers.DateField(default=timezone.now().date(), required=False)
    items = MenuItemSerializer(many=True, required=False)

    class Meta:
        model = Menu
        fields = ["id", "date", "is_published", "items"]
        read_only_fields = ["restaurant"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        restaurant = self.context["request"].user
        date = validated_data["date"]

        # Check if a menu already exists for this restaurant and date
        if Menu.objects.filter(restaurant=restaurant, date=date).exists():
            raise serializers.ValidationError(
                "A menu for this date already exists for your restaurant."
                +
                "Create a new menu for a different date or with different"
                +
                "restaurant."
            )

        # Remove 'restaurant' from validated_data if it exists
        validated_data.pop("restaurant", None)

        menu = Menu.objects.create(restaurant=restaurant, **validated_data)

        for item_data in items_data:
            MenuItem.objects.create(menu=menu, **item_data)
        return menu

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        menu = super().update(instance, validated_data)

        if items_data is not None:
            # Remove existing items not in the update data
            menu.items.exclude(
                id__in=[item.get("id")
                        for item in items_data if item.get("id")]
            ).delete()

            for item_data in items_data:
                item_id = item_data.get("id")
                if item_id:
                    MenuItem.objects.filter(id=item_id, menu=menu).update(
                        **item_data)
                else:
                    MenuItem.objects.create(menu=menu, **item_data)

        return menu

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["items"] = MenuItemSerializer(
            instance.items.all(), many=True
        ).data
        return representation

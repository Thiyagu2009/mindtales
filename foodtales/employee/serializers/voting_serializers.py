from rest_framework import serializers
from restaurant.models import Menu
from employee.models import Vote
from django.utils import timezone
from django.db import transaction


class OldVoteSerializer(serializers.ModelSerializer):
    menu = serializers.UUIDField()

    class Meta:
        model = Vote
        fields = ["menu"]

    def validate(self, data):
        user = self.context["request"].user
        today = timezone.now().date()

        if Vote.objects.filter(user=user, created_at__date=today).exists():
            raise serializers.ValidationError("You have already voted today.")

        # Fetch the Menu instance using the provided UUID
        try:
            menu = Menu.objects.get(id=data["menu"])
            data["menu"] = menu
        except Menu.DoesNotExist:
            raise serializers.ValidationError("Invalid menu ID.")

        return data

    def create(self, validated_data):
        validated_data["rank"] = 1  # Old version always creates a top rank vote
        return super().create(validated_data)


class VoteItem(serializers.Serializer):
    menu = serializers.UUIDField()
    points = serializers.IntegerField(min_value=1, max_value=3)


class NewVoteSerializer(serializers.Serializer):
    votes = VoteItem(many=True, allow_empty=False)

    def validate_votes(self, value):
        user = self.context["request"].user
        today = timezone.now().date()
        if len(value) != 3:
            raise serializers.ValidationError("You must provide exactly 3 votes.")

        menu_ids = [vote["menu"] for vote in value]
        if len(set(menu_ids)) != 3:
            raise serializers.ValidationError("You must vote for 3 different menus.")

        points = [vote["points"] for vote in value]
        if sorted(points) != [1, 2, 3]:
            raise serializers.ValidationError(
                "You must assign points 1, 2, and 3 to your votes."
            )

        # Validate that all menu UUIDs exist
        existing_menus = Menu.objects.filter(id__in=menu_ids)
        if existing_menus.count() != 3:
            raise serializers.ValidationError("One or more menu IDs are invalid.")
        if Vote.objects.filter(user=user, created_at__date=today).exists():
            raise serializers.ValidationError("You have already voted today.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        votes = []
        print(f"Creating votes for user: {user}")
        for vote_data in validated_data["votes"]:
            print(f"Creating vote: {vote_data}")
            try:
                vote = Vote.objects.create(
                    user=user,
                    menu_id=vote_data["menu"],
                    rank=4 - vote_data["points"],
                )
                votes.append(vote)
                print(f"Vote created: {vote}")
            except Exception as e:
                print(f"Error creating vote: {e}")
        return votes

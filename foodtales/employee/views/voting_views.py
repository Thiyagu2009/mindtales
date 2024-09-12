import logging

from rest_framework import generics, permissions, status
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Sum, Case, When, IntegerField


from employee.serializers.voting_serializers import (
    NewVoteSerializer,
    OldVoteSerializer,
)
from foodtales.utils import success_response, error_response
from restaurant.serializers.restaurant_serializers import (
    MenuWithVotesSerializer,
)
from user.permissions import IsEmployee
from restaurant.models import Menu
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("foodtales")


class SubmitVoteView(generics.CreateAPIView):
    """
    API view to submit a vote for a menu item.
    """

    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def get_serializer_class(self):
        if self.request.app_version >= "2.0":
            return NewVoteSerializer
        return OldVoteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            vote = serializer.save(user=request.user)
            logger.info(f"Vote submitted successfully: {vote.id}")
            return success_response(
                message="Vote submitted successfully",
                data=None,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            logger.error(f"Vote submission failed: {e.detail}")
            return error_response(
                message="Vote submission failed", errors=e.detail)
        except ObjectDoesNotExist as e:
            logger.error(f"Vote submission failed: {str(e)}")
            return error_response(
                message="Vote submission failed", errors=str(e))
        except Exception as e:
            logger.error(f"Vote submission failed: {str(e)}")
            return error_response(
                message="Vote submission failed", errors=str(e))


class VoteResultsView(generics.ListAPIView):
    """
    API view to fetch the voting results for the current day.
    """

    serializer_class = MenuWithVotesSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def get_queryset(self):
        today = timezone.now().date()
        logger.info(f"Fetching voting results for today: {today}")
        limit = self.request.query_params.get(
            "limit", 3
        )  # Default to top 3 if not specified
        try:
            limit = int(limit)
        except ValueError:
            limit = 3  # Default to 3 if an invalid value is provided
        return (
            Menu.objects.filter(date=today, is_published=True)
            .select_related("restaurant")
            .prefetch_related("items")
            .annotate(
                total_points=Sum(
                    Case(
                        When(votes__rank=1, then=3),
                        When(votes__rank=2, then=2),
                        When(votes__rank=3, then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                )
            )
            .order_by("-total_points")
            .filter(total_points__gt=0)[:limit]
        )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return success_response(
                    message="No voting results available for today.",
                    status_code=status.HTTP_404_NOT_FOUND,
                    data=None,
                )

            serializer = self.get_serializer(queryset, many=True)
            logger.info(
                f"Voting results fetched successfully: {serializer.data}")
            return success_response(
                message="Voting results fetched successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(
                f"An error occurred while fetching voting results: {str(e)}")
            return error_response(
                {
                    "detail": f"An error occurred while fetching voting \
                    results: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

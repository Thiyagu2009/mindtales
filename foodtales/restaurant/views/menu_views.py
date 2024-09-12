import logging

from rest_framework import generics, permissions, status, serializers
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from restaurant.serializers.menu_items_serializers import MenuSerializer
from ..models import Menu
from ..serializers.restaurant_serializers import MenuWithRestaurantSerializer
from user.permissions import IsEmployee, IsRestaurantUser
from foodtales.utils import CustomPageNumberPagination, success_response, \
    error_response

logger = logging.getLogger("foodtales")


class MenuCreateView(generics.CreateAPIView):
    """
    API view to create a new menu.
    """

    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantUser]

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"Menu created successfully: {response.data}")
            return success_response(
                message="Menu Created Successfully",
                data=response.data,
                status_code=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            logger.error(f"Menu creation failed: {e.detail}")
            return error_response(message="Menu creation failed",
                                  errors=e.detail)

        except Exception as e:
            logger.error(f"Menu creation failed: {str(e)}")
            return error_response(
                message="Menu Creation Failed",
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user)


# Not Used
class MenuRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated, IsRestaurantUser]

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return success_response(data=response.data)
        except ObjectDoesNotExist:
            return error_response(
                message="Menu not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return success_response(data=response.data)
        except Exception as e:
            return error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
            return success_response(message="Menu deleted successfully.")
        except Exception as e:
            return error_response(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )


class AllRestaurantsCurrentDayMenuView(generics.ListAPIView):
    """
    API view to fetch the current day's menu for all restaurants.
    """

    serializer_class = MenuWithRestaurantSerializer
    permission_classes = [permissions.AllowAny, IsEmployee]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        today = timezone.now().date()
        return Menu.objects.filter(
            date=today, is_published=True).select_related(
            "restaurant"
        )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return success_response(
                    message="No menus available for today.")

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = {
                    "count": result.data["count"],
                    "next": result.data["next"],
                    "previous": result.data["previous"],
                    "results": result.data["results"],
                }
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            logger.info(
                f"Today's menu fetched successfully. Total menus: \
                {len(data['results'] if page else data)}"
            )
            return success_response(
                message="Today's menu fetched successfully", data=data
            )
        except Exception as e:
            logger.error(f"Unable to fetch today's menu: {str(e)}")
            return error_response(
                message="Unable to fetch today's menu",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

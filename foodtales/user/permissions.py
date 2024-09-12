# In a new file, e.g., permissions.py

from rest_framework.permissions import BasePermission


class IsRestaurantUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "restaurant"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "employee"


# from rest_framework.views import APIView
# from .permissions import IsRestaurant, IsEmployee


# class RestaurantOnlyView(APIView):
#     permission_classes = [IsRestaurant]
#     # Your view logic here


# class EmployeeOnlyView(APIView):
#     permission_classes = [IsEmployee]
#     # Your view logic here

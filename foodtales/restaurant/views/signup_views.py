from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from foodtales.utils import success_response, error_response
from restaurant.serializers.signup_serializers import \
    RestaurantSignUpSerializer


class RestaurantSignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RestaurantSignUpSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return success_response(
                    message="Restaurant Created Successfully",
                    data={
                        "refresh_token": str(refresh),
                        "access_token": str(refresh.access_token),
                    },
                    status_code=status.HTTP_201_CREATED,
                )
            return error_response(
                message="Restaurant Creation Failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return error_response(
                message="Restaurant Creation Failed",
                errors="Unexpected Error Occurred",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

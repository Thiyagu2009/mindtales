import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from employee.serializers.signup_serializers import EmployeeSignUpSerializer
from foodtales.utils import error_response, success_response

logger = logging.getLogger("foodtales")


class EmployeeSignUpView(APIView):
    """
    API view for employee signup.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployeeSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info(f"Employee registered successfully: {user.email}")
            return success_response(
                message="Employee registered successfully",
                data={
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                },
                status_code=status.HTTP_201_CREATED,
            )
        logger.error(f"Employee registration failed: {serializer.errors}")
        return error_response("Employee Registration Failed", serializer.errors)

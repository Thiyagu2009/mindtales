from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination


def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    response = {
        "success": True,
        "message": message or "Operation successful",
        "data": data,
    }
    return Response(response, status=status_code)


def error_response(message, errors=None,
                   status_code=status.HTTP_400_BAD_REQUEST):
    response = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else {},
    }

    # If errors is a dict with a single key 'non_field_errors',
    # move it to the top level
    if isinstance(errors, dict) and "non_field_errors" in errors:
        response["errors"] = errors["non_field_errors"]

    # If errors is a list, assume it's a list of error messages
    elif isinstance(errors, list):
        response["errors"] = {"general": errors}

    # If errors is a string, put it in a 'general' key
    elif isinstance(errors, str):
        response["errors"] = {"general": [errors]}

    return Response(response, status=status_code)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

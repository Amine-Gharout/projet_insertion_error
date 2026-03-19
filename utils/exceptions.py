from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "status_code": response.status_code,
            "data": None,
            "message": str(exc),
            "errors": response.data,
        }
        return Response(custom_response, status=response.status_code)

    return response
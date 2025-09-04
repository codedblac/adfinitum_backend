from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom global exception handler for DRF.
    Ensures all errors return JSON responses with a consistent format.
    """
    # First, get the standard error response from DRF
    response = exception_handler(exc, context)

    if response is not None:
        # Format DRF validation and API errors
        return Response(
            {
                "errors": response.data,
                "status_code": response.status_code
            },
            status=response.status_code
        )

    # Handle non-DRF errors (e.g. unexpected exceptions)
    return Response(
        {
            "errors": {"detail": str(exc)},
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

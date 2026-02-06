import logging

from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    ValidationError,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global exception handler for Django Rest Framework.

    Provides:
    - Consistent error response structure
    - Proper HTTP status codes
    - Safe error messages in production
    - Extra debugging details in DEBUG mode
    """

    # First let DRF handle what it knows
    
    response = exception_handler(exc, context)

    request = context.get("request")
    view = context.get("view")

    if response is not None:
        return _format_drf_error_response(
            response=response,
            exc=exc,
            request=request,
            view=view,
        )

    # Handle Django-level exceptions
    if isinstance(exc, Http404):
        return _error_response(
            message="Not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            exc=exc,
            request=request,
        )

    if isinstance(exc, (PermissionDenied, DRFPermissionDenied)):
        return _error_response(
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
            exc=exc,
            request=request,
        )

    if isinstance(exc, DjangoValidationError):
        return _error_response(
            message=exc.message_dict if hasattr(exc, "message_dict") else exc.messages,
            status_code=status.HTTP_400_BAD_REQUEST,
            exc=exc,
            request=request,
        )

    # Unhandled exceptions (500)
    
    logger.exception("Unhandled exception occurred", exc_info=exc)

    return _error_response(
        message="An unexpected error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        exc=exc,
        request=request,
        expose_detail=settings.DEBUG,
    )


def _format_drf_error_response(response, exc, request=None, view=None):
    """
    Format DRF-generated exceptions into a unified response schema.
    """
    error_message = response.data

    return Response(
        {
            "success": False,
            "error": {
                "message": error_message,
                "type": exc.__class__.__name__,
            },
            "meta": _build_meta(request, response.status_code, view),
        },
        status=response.status_code,
    )


def _error_response(
    message,
    status_code,
    exc=None,
    request=None,
    expose_detail=False,
):
    """
    Build a standardized error response.
    """
    error_payload = {
        "message": message,
        "type": exc.__class__.__name__ if exc else None,
    }

    if expose_detail:
        error_payload["detail"] = str(exc)

    return Response(
        {
            "success": False,
            "error": error_payload,
            "meta": _build_meta(request, status_code),
        },
        status=status_code,
    )


def _build_meta(request, status_code, view=None):
    """
    Build metadata section for error responses.
    """
    meta = {
        "status_code": status_code,
    }

    if request:
        meta.update(
            {
                "path": request.path,
                "method": request.method,
            }
        )

    if view:
        meta["view"] = view.__class__.__name__

    return meta

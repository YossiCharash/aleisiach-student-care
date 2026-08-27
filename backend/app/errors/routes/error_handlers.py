from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.errors.service.app_error import AppError
from backend.app.schema.routes.error_response import ErrorResponse
from backend.app.schema.routes.field_error import FieldError
from backend.app.service.alerts.error_alert_service import ErrorAlertService

_UNEXPECTED_MESSAGE = "אירעה שגיאה בלתי צפויה. הצוות קיבל התראה. אנא נסו שוב מאוחר יותר."
_VALIDATION_MESSAGE = "הנתונים שנשלחו אינם תקינים."
_HTTP_MESSAGES: dict[int, str] = {
    400: "הבקשה אינה תקינה.",
    401: "נדרשת התחברות.",
    403: "אין לך הרשאה לפעולה זו.",
    404: "המשאב המבוקש לא נמצא.",
    405: "הפעולה אינה נתמכת.",
    409: "הפעולה מתנגשת עם המצב הקיים.",
}
_HTTP_FALLBACK_MESSAGE = "הבקשה נכשלה."


def _json(status_code: int, body: ErrorResponse) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return _json(error.status_code, ErrorResponse(code=error.code, message=error.message))


async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    fields = [
        FieldError(field=".".join(str(part) for part in item["loc"]), message=item["msg"])
        for item in error.errors()
    ]
    body = ErrorResponse(code="validation_error", message=_VALIDATION_MESSAGE, fields=fields)
    return _json(422, body)


async def handle_http_exception(request: Request, error: StarletteHTTPException) -> JSONResponse:
    message = _HTTP_MESSAGES.get(error.status_code, _HTTP_FALLBACK_MESSAGE)
    return _json(error.status_code, ErrorResponse(code="http_error", message=message))


async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    reference = _report(request, error)
    body = ErrorResponse(code="internal_error", message=_UNEXPECTED_MESSAGE, reference=reference)
    return _json(500, body)


def _report(request: Request, error: Exception) -> str | None:
    service = _alert_service(request)
    if service is None:
        return None
    return service.report(error, request.method, request.url.path)


def _alert_service(request: Request) -> ErrorAlertService | None:
    bootstrap = getattr(request.app.state, "bootstrap", None)
    if not isinstance(bootstrap, Bootstrap):
        return None
    return bootstrap.error_alert_service


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, handle_unexpected_error)

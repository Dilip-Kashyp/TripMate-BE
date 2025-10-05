from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.utils.responses import Response_handler
from fastapi.exceptions import RequestValidationError
from app.core.logger import logger


class AppException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, message: str, status_code: int = 400, data: dict = None):
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(message)


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=Response_handler(
            success=False,
            message=exc.message,
            data=exc.data,
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"⚠️ Validation Error at {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=Response_handler(
            success=False,
            message="Validation error",
            data={"errors": exc.errors()}
        )
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Response_handler(
            success=False,
            message="Internal Server Error",
        )
    )

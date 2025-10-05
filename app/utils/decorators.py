import inspect
import functools
from fastapi.responses import JSONResponse
from app.utils.responses import Response_handler
from app.core.logger import logger


def Response(success_message: str = "Success"):
    """
    Decorator to standardize API responses.
    Handles both async and sync route handlers safely.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if the function is async or sync
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # If already standardized, return directly
                if isinstance(result, dict) and {"success", "message", "data"} <= result.keys():
                    return JSONResponse(content=result)

                return JSONResponse(
                    content=Response_handler(True, success_message, result)
                )
            except Exception as e:
                logger.exception(f"🔥 Error in {func.__name__}: {e}")
                raise e  # Let global exception handler catch it
        return wrapper
    return decorator

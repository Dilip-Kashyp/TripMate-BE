from typing import Any, Optional

def Response_handler(success: bool, message: str, data: Optional[Any] = None):
    return {
        "success": success,
        "message": message,
        "data": data or {}
    }

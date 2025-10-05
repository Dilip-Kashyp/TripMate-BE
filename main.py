from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import  setup_middlewares
from app.core.logger import logger
from fastapi.exceptions import RequestValidationError
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler
)

app = FastAPI(
    title="Routes API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
setup_middlewares(app)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
    
app.include_router(api_router, prefix=settings.API_V1_STR)
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")
    
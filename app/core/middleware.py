from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.core.logger import logger
import time

def setup_middlewares(app: FastAPI):
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or restrict to your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Middleware: Log requests
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = round(time.time() - start_time, 3)
        logger.info(f"{request.method} {request.url.path} - {response.status_code} [{process_time}s]")
        return response

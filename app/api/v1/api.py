from fastapi import APIRouter
from app.api.v1.endpoints import planner, route

api_router = APIRouter()
api_router.include_router(planner.router, tags=["planner"])
api_router.include_router(route.router, tags=["planner"])
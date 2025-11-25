from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field
from app.constants.agent_constant import ERROR_STATE, INVOKE_AGENT_STATE
from services.agent_orchestrator import TravelAgentOrchestrator
from tools.rail_tool import search_trains, search_station_code
from app.core.logger import logger
from typing import Optional, List

router = APIRouter()
agent = TravelAgentOrchestrator()

class TripPlanRequest(BaseModel):
    """Request model for trip planning"""
    query: str = Field(..., description="Natural language query for trip planning", 
                       example="I want to travel from Delhi to Mumbai tomorrow morning")
    
class DirectTrainRequest(BaseModel):
    """Request model for direct train search"""
    from_station: str = Field(..., description="Source station code", example="NDLS")
    to_station: str = Field(..., description="Destination station code", example="BCT")
    hours: Optional[int] = Field(24, description="Time window in hours", ge=1, le=72)

class ConversationRequest(BaseModel):
    """Request model for conversational queries"""
    message: str = Field(..., description="User message")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Previous messages")

@router.post("/plan-trip")
async def plan_trip(request: TripPlanRequest):
    try:
        logger.info(f"{INVOKE_AGENT_STATE} {request.query}")
        result = agent.plan_trip(request.query)
        return result
        
    except Exception as e:
        logger.error(f"{ERROR_STATE} {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"{ERROR_STATE} {str(e)}",
        }

@router.post("/trains/search",
             summary="Direct Train Search",
             description="Search for trains between two stations using station codes")
async def search_trains_direct(request: DirectTrainRequest):
    """
    Direct API to search trains between stations (bypasses AI agent)
    
    Use this when you already know the exact station codes.
    For automatic station code lookup, use /plan-trip instead.
    """
    try:
        result = search_trains.invoke({
            "from_station": request.from_station,
            "to_station": request.to_station,
            "hours": request.hours
        })
        return result
        
    except Exception as e:
        logger.error(f"Error in direct train search: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/stations/search",
            summary="Search Station Codes",
            description="Find station codes by city or station name")
async def search_stations(
    query: str = Query(..., description="City or station name to search", example="Mumbai")
):
    """
    Search for station codes by name
    
    Useful for finding the correct station code before using /trains/search
    """
    try:
        result = search_station_code.invoke({"station_name": query})
        return result
        
    except Exception as e:
        logger.error(f"Error searching stations: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/workflow/visualization",
            summary="View Workflow Graph",
            description="Get a visualization of the LangGraph workflow")
async def get_workflow_visualization():
    """
    Returns a text representation of the LangGraph workflow
    
    Shows how the agent processes queries through different nodes
    """
    return {
        "success": True,
        "workflow": agent.get_graph_visualization()
    }

@router.get("/health",
            summary="Health Check",
            description="Check if the API is running")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "TripMate AI Backend (LangChain + LangGraph)",
        "features": [
            "Natural language trip planning",
            "AI-powered recommendations",
            "Real-time train data",
            "Intelligent intent extraction",
            "Multi-step workflow orchestration"
        ]
    }

@router.get("/",
            summary="API Info",
            description="Get information about the API")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TripMate AI Travel API",
        "version": "2.0.0",
        "framework": "LangChain + LangGraph",
        "description": "Intelligent train travel planning powered by Google Gemini",
        "endpoints": {
            "main": "/api/v1/plan-trip",
            "direct_search": "/api/v1/trains/search",
            "station_search": "/api/v1/stations/search",
            "workflow": "/api/v1/workflow/visualization",
            "docs": "/docs"
        }
    }
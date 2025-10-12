"""
State definition for the travel planning agent workflow
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class TravelPlannerState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    Each node can read and modify this state.
    """
    # User input
    user_query: str
    
    # Extracted intent
    from_location: Optional[str]
    to_location: Optional[str]
    from_station_code: Optional[str]
    to_station_code: Optional[str]
    travel_date: Optional[str]
    time_preference: Optional[str]  # morning, afternoon, evening, night, any
    budget_preference: Optional[str]  # budget, standard, premium, any
    direct_only: bool
    
    # Fetched data
    available_trains: List[Dict[str, Any]]
    total_trains: int
    
    # Analysis results
    filtered_trains: List[Dict[str, Any]]
    top_recommendations: List[Dict[str, Any]]
    
    # AI-generated insights
    ai_recommendation: str
    reasoning: str
    
    # Workflow control
    current_step: str
    error: Optional[str]
    needs_clarification: bool
    clarification_message: Optional[str]
    
    # Metadata
    processing_time: float
    timestamp: str
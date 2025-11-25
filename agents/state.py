from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class TravelPlannerState(TypedDict):
    user_query: str
    
    from_location: Optional[str]
    to_location: Optional[str]
    from_station_code: Optional[str]
    to_station_code: Optional[str]
    travel_date: Optional[str]
    time_preference: Optional[str]  
    budget_preference: Optional[str]  
    direct_only: bool
    
    available_trains: List[Dict[str, Any]]
    total_trains: int
    
    filtered_trains: List[Dict[str, Any]]
    top_recommendations: List[Dict[str, Any]]
    
    ai_recommendation: str
    reasoning: str
    
    current_step: str
    error: Optional[str]
    needs_clarification: bool
    clarification_message: Optional[str]
    
    processing_time: float
    timestamp: str
"""
Agent orchestrator using LangGraph for intelligent travel planning
"""
from agents.travel_graph import travel_planner_graph
from agents.state import TravelPlannerState
from app.core.logger import logger
from typing import Dict, Any
import time

class TravelAgentOrchestrator:
    """
    High-level orchestrator that manages the LangGraph workflow
    """
    
    def __init__(self):
        self.graph = travel_planner_graph
        logger.info("TravelAgentOrchestrator initialized with LangGraph")
    
    def plan_trip(self, user_query: str) -> Dict[str, Any]:
        """
        Main method to process user query through the LangGraph workflow
        
        Args:
            user_query: Natural language query from user
        
        Returns:
            Dictionary with recommendations and travel details
        """
        logger.info(f"Processing trip planning request: {user_query}")
        start_time = time.time()
        
        # Initialize state
        initial_state: TravelPlannerState = {
            "user_query": user_query,
            "from_location": None,
            "to_location": None,
            "from_station_code": None,
            "to_station_code": None,
            "travel_date": None,
            "time_preference": None,
            "budget_preference": None,
            "direct_only": False,
            "available_trains": [],
            "total_trains": 0,
            "filtered_trains": [],
            "top_recommendations": [],
            "ai_recommendation": "",
            "reasoning": "",
            "current_step": "initialized",
            "error": None,
            "needs_clarification": False,
            "clarification_message": None,
            "processing_time": 0.0,
            "timestamp": ""
        }
        
        try:
            # Execute the graph
            logger.info("Executing LangGraph workflow...")
            final_state = self.graph.invoke(initial_state)
            
            processing_time = time.time() - start_time
            logger.info(f"Workflow completed in {processing_time:.2f}s")
            
            # Format response
            return self._format_response(final_state, processing_time)
            
        except Exception as e:
            logger.error(f"Error in plan_trip: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"An error occurred during trip planning: {str(e)}",
                "query": user_query
            }
    
    def _format_response(self, state: TravelPlannerState, processing_time: float) -> Dict[str, Any]:
        """
        Format the final state into a clean API response
        """
        # Check for errors
        if state.get("error"):
            return {
                "success": False,
                "error": state["error"],
                "query": state.get("user_query")
            }
        
        # Check if clarification is needed
        if state.get("needs_clarification"):
            return {
                "success": False,
                "needs_clarification": True,
                "message": state.get("clarification_message"),
                "query": state.get("user_query")
            }
        
        # Successful response
        return {
            "success": True,
            "query": state.get("user_query"),
            "intent": {
                "from_location": state.get("from_location"),
                "to_location": state.get("to_location"),
                "from_station": state.get("from_station_code"),
                "to_station": state.get("to_station_code"),
                "travel_date": state.get("travel_date"),
                "time_preference": state.get("time_preference"),
                "budget_preference": state.get("budget_preference"),
                "direct_only": state.get("direct_only")
            },
            "results": {
                "total_trains_found": state.get("total_trains", 0),
                "filtered_trains_count": len(state.get("filtered_trains", [])),
                "top_recommendations": state.get("top_recommendations", [])[:3],
                "all_filtered_trains": state.get("filtered_trains", [])[:10]
            },
            "ai_analysis": {
                "recommendation": state.get("ai_recommendation"),
                "reasoning": state.get("reasoning")
            },
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "workflow_step": state.get("current_step"),
                "timestamp": state.get("timestamp")
            }
        }
    
    def get_graph_visualization(self) -> str:
        """
        Get a text representation of the workflow graph
        """
        return """
Travel Planning Workflow Graph:
================================

[User Query]
     ↓
[Extract Intent] → Extract locations, preferences
     ↓
[Validate Locations] → Get station codes
     ↓
[Fetch Trains] → Query IRCTC API
     ↓
[Analyze Trains] → Filter by preferences
     ↓
[Generate Recommendations] → AI analysis
     ↓
[Final Response]

Conditional Edges:
- If error at any step → END with error
- If needs clarification → END with clarification request
- If successful → Continue to next step
"""
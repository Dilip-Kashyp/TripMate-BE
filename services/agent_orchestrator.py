from copy import deepcopy
from agents.travel_graph import travel_planner_graph
from agents.state import TravelPlannerState
from app.constants.agent_constant import (
    COMPLETE_STATE_TIME,
    ERROR_STATE,
    EXECUTING_STATE,
    INITIALIZED_STATE,
    PROCESSING_STATE,
)
from app.constants.common import WORKFLOW_DESCRIPTION
from app.core.logger import logger
from typing import Dict, Any
import time
from schemas.travel_planner_schemas import DEFAULT_TRAVEL_STATE


class TravelAgentOrchestrator:
    def __init__(self):
        self.graph = travel_planner_graph
        logger.info(INITIALIZED_STATE)

    def plan_trip(self, user_query: str) -> Dict[str, Any]:
        try:
            logger.info(f"{PROCESSING_STATE} {user_query}")
            start_time = time.time()

            initial_state = deepcopy(DEFAULT_TRAVEL_STATE)
            initial_state["user_query"] = user_query

            logger.info(EXECUTING_STATE)
            final_state = self.graph.invoke(initial_state)

            processing_time = time.time() - start_time
            logger.info(f"{COMPLETE_STATE_TIME} {processing_time:.2f}s")

            return self._format_response(final_state, processing_time)

        except Exception as e:
            logger.error(f"{ERROR_STATE} {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"{ERROR_STATE} {str(e)}",
                "query": user_query,
            }

    def _format_response(
        self, state: TravelPlannerState, processing_time: float
    ) -> Dict[str, Any]:
        if state.get("error"):
            return {
                "success": False,
                "error": state["error"],
                "query": state.get("user_query"),
            }

        if state.get("needs_clarification"):
            return {
                "success": False,
                "needs_clarification": True,
                "message": state.get("clarification_message"),
                "query": state.get("user_query"),
            }

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
                "direct_only": state.get("direct_only"),
            },
            "results": {
                "total_trains_found": state.get("total_trains", 0),
                "filtered_trains_count": len(state.get("filtered_trains", [])),
                "top_recommendations": state.get("top_recommendations", [])[:3],
                "all_filtered_trains": state.get("filtered_trains", [])[:10],
            },
            "ai_analysis": {
                "recommendation": state.get("ai_recommendation"),
                "reasoning": state.get("reasoning"),
            },
            "metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "workflow_step": state.get("current_step"),
                "timestamp": state.get("timestamp"),
            },
        }

    def get_graph_visualization(self) -> str:
        return WORKFLOW_DESCRIPTION
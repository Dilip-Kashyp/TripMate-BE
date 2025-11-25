import os
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.state import TravelPlannerState
from app.constants.agent_constant import EXTRACTING_INTENT_ERROR, EXTRACTING_INTENT_NODE
from app.constants.prompts import TRAVEL_INTENT_PROMPT
from tools.rail_tool import search_trains, get_station_code_from_city
from app.core.config import settings
from app.core.logger import logger
from datetime import datetime
import time
from typing import Dict, Any
import json


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_output_tokens=1024,
    transport="rest",  
    google_api_key=settings.GOOGLE_API_KEY
)

def extract_intent_node(state: TravelPlannerState) -> Dict[str, Any]:
    try:
        logger.info(EXTRACTING_INTENT_NODE)
        start_time = time.time()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", TRAVEL_INTENT_PROMPT),
            ("user", "Extract intent from: {query}")
        ])
    
        chain = prompt | llm | JsonOutputParser()
        intent = chain.invoke({"query": state["user_query"]})
        
        processing_time = time.time() - start_time
        
        return {
            **state,
            "from_location": intent.get("from_location"),
            "to_location": intent.get("to_location"),
            "travel_date": intent.get("travel_date", "today"),
            "time_preference": intent.get("time_preference", "any"),
            "budget_preference": intent.get("budget_preference", "any"),
            "direct_only": intent.get("direct_only", False),
            "current_step": "intent_extracted",
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"{EXTRACTING_INTENT_ERROR} {str(e)}")
        return {
            **state,
            "error": f"{EXTRACTING_INTENT_ERROR} {str(e)}",
            "current_step": "error"
        }

def validate_locations_node(state: TravelPlannerState) -> Dict[str, Any]:
    logger.info("")
    
    from_loc = state.get("from_location")
    to_loc = state.get("to_location")
    
    # Check if we have both locations
    if not from_loc or not to_loc:
        return {
            **state,
            "needs_clarification": True,
            "clarification_message": "Please specify both source and destination cities.",
            "current_step": "needs_clarification"
        }
    
    # Get station codes using the tool
    try:
        from_code = get_station_code_from_city.invoke(from_loc)
        to_code = get_station_code_from_city.invoke(to_loc)
        
        logger.info(f"Station codes: {from_loc} -> {from_code}, {to_loc} -> {to_code}")
        
        return {
            **state,
            "from_station_code": from_code,
            "to_station_code": to_code,
            "current_step": "locations_validated",
            "needs_clarification": False
        }
        
    except Exception as e:
        logger.error(f"Location validation error: {str(e)}")
        return {
            **state,
            "error": f"Failed to validate locations: {str(e)}",
            "current_step": "error"
        }

def fetch_trains_node(state: TravelPlannerState) -> Dict[str, Any]:
    """
    Node 3: Fetch available trains using LangChain tool
    """
    logger.info("Node: Fetching train data")
    
    from_code = state.get("from_station_code")
    to_code = state.get("to_station_code")
    
    if not from_code or not to_code:
        return {
            **state,
            "error": "Missing station codes",
            "current_step": "error"
        }
    
    try:
        # Use the LangChain tool to fetch trains
        result = search_trains.invoke({
            "from_station": from_code,
            "to_station": to_code,
            "hours": 24
        })
        
        if not result.get("success"):
            return {
                **state,
                "error": result.get("error", "Failed to fetch trains"),
                "current_step": "error"
            }
        
        trains = result.get("trains", [])
        
        return {
            **state,
            "available_trains": trains,
            "total_trains": len(trains),
            "current_step": "trains_fetched"
        }
        
    except Exception as e:
        logger.error(f"Train fetching error: {str(e)}")
        return {
            **state,
            "error": f"Failed to fetch trains: {str(e)}",
            "current_step": "error"
        }

def analyze_trains_node(state: TravelPlannerState) -> Dict[str, Any]:
    """
    Node 4: Analyze and filter trains based on preferences
    """
    logger.info("Node: Analyzing trains")
    
    trains = state.get("available_trains", [])
    time_pref = state.get("time_preference", "any")
    
    if not trains:
        return {
            **state,
            "filtered_trains": [],
            "current_step": "no_trains_found",
            "error": "No trains available for this route"
        }
    
    # Filter trains based on time preference
    filtered = trains
    if time_pref != "any":
        filtered = [t for t in trains if _matches_time_preference(t, time_pref)]
    
    # Sort by departure time
    try:
        filtered.sort(key=lambda x: x.get("from_std", "00:00"))
    except:
        pass
    
    return {
        **state,
        "filtered_trains": filtered,
        "current_step": "trains_analyzed"
    }

def _matches_time_preference(train: Dict, time_pref: str) -> bool:
    """Helper to match train time with preference"""
    try:
        dept_time = train.get("from_std", "00:00")
        hour = int(dept_time.split(":")[0])
        
        if time_pref == "morning" and 6 <= hour < 12:
            return True
        elif time_pref == "afternoon" and 12 <= hour < 17:
            return True
        elif time_pref == "evening" and 17 <= hour < 21:
            return True
        elif time_pref == "night" and (hour >= 21 or hour < 6):
            return True
        return False
    except:
        return True

def generate_recommendations_node(state: TravelPlannerState) -> Dict[str, Any]:
    """
    Node 5: Generate AI-powered recommendations using LLM
    """
    logger.info("Node: Generating AI recommendations")
    
    filtered_trains = state.get("filtered_trains", [])
    
    if not filtered_trains:
        return {
            **state,
            "ai_recommendation": "No trains found matching your preferences. Try adjusting your search criteria.",
            "reasoning": "No trains available",
            "top_recommendations": [],
            "current_step": "completed"
        }
    
    # Prepare train data for LLM (top 5)
    top_trains = filtered_trains[:5]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert Indian Railways travel advisor. Analyze the available trains and provide personalized recommendations.
            Consider:
            1. Departure and arrival times
            2. Journey duration
            3. Train type and class
            4. User's time preferences

            Provide:
            - Top 3 train recommendations with clear reasoning
            - Pros and cons of each option
            - Best overall choice

            Be concise, friendly, and practical."""),
            ("user", """User preferences:
            - From: {from_location} ({from_code})
            - To: {to_location} ({to_code})
            - Time preference: {time_pref}
            - Budget: {budget_pref}
                Available trains:
                {trains_data}
            Provide your recommendations:""")
    ])
    
    try:
        trains_data = "\n".join([
            f"Train {i+1}: {t.get('train_name', 'N/A')} ({t.get('train_number', 'N/A')}) - "
            f"Departs: {t.get('from_std', 'N/A')}, Arrives: {t.get('to_std', 'N/A')}, "
            f"Duration: {t.get('duration', 'N/A')}"
            for i, t in enumerate(top_trains)
        ])
        
        chain = prompt | llm
        recommendation = chain.invoke({
            "from_location": state.get("from_location"),
            "from_code": state.get("from_station_code"),
            "to_location": state.get("to_location"),
            "to_code": state.get("to_station_code"),
            "time_pref": state.get("time_preference"),
            "budget_pref": state.get("budget_preference"),
            "trains_data": trains_data
        })
        
        return {
            **state,
            "ai_recommendation": recommendation.content,
            "top_recommendations": top_trains[:3],
            "reasoning": "Analysis based on departure times, duration, and user preferences",
            "current_step": "completed"
        }
        
    except Exception as e:
        logger.error(f"Recommendation generation error: {str(e)}")
        return {
            **state,
            "ai_recommendation": "Here are the available trains. Please review the options above.",
            "top_recommendations": top_trains[:3],
            "reasoning": "Basic listing due to processing error",
            "current_step": "completed"
        }

def should_continue(state: TravelPlannerState) -> str:
    """
    Router function to determine next node based on state
    """
    current_step = state.get("current_step", "")
    
    if state.get("error"):
        return "error"
    
    if state.get("needs_clarification"):
        return "clarification"
    
    if current_step == "intent_extracted":
        return "validate_locations"
    elif current_step == "locations_validated":
        return "fetch_trains"
    elif current_step == "trains_fetched":
        return "analyze_trains"
    elif current_step == "trains_analyzed":
        return "generate_recommendations"
    elif current_step == "completed":
        return END
    else:
        return END

# Build the graph
def create_travel_planning_graph():
    """
    Create the LangGraph workflow for travel planning
    """
    workflow = StateGraph(TravelPlannerState)
    
    # Add nodes
    workflow.add_node("extract_intent", extract_intent_node)
    workflow.add_node("validate_locations", validate_locations_node)
    workflow.add_node("fetch_trains", fetch_trains_node)
    workflow.add_node("analyze_trains", analyze_trains_node)
    workflow.add_node("generate_recommendations", generate_recommendations_node)
    
    # Set entry point
    workflow.set_entry_point("extract_intent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "extract_intent",
        should_continue,
        {
            "validate_locations": "validate_locations",
            "error": END,
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "validate_locations",
        should_continue,
        {
            "fetch_trains": "fetch_trains",
            "clarification": END,
            "error": END,
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "fetch_trains",
        should_continue,
        {
            "analyze_trains": "analyze_trains",
            "error": END,
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "analyze_trains",
        should_continue,
        {
            "generate_recommendations": "generate_recommendations",
            "error": END,
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_recommendations",
        should_continue,
        {
            END: END
        }
    )
    
    return workflow.compile()

# Create the compiled graph
travel_planner_graph = create_travel_planning_graph()
logger.info("Travel planning graph created successfully")
"""
LangChain tools for railway data fetching
"""
from langchain.tools import tool
from typing import Dict, Any, List
import requests
from app.core.config import settings
from app.core.logger import logger

@tool
def search_trains(from_station: str, to_station: str, hours: int = 24) -> Dict[str, Any]:
    """
    Search for trains between two stations. Use this tool when you need to find available trains.
    
    Args:
        from_station: Source station code (e.g., 'NDLS' for New Delhi, 'HYB' for Hyderabad)
        to_station: Destination station code (e.g., 'BCT' for Mumbai, 'SBC' for Bangalore)
        hours: Time window in hours to search for trains (default: 24)
    
    Returns:
        Dictionary containing train information including departure times, arrival times, duration, and train details
    """
    try:
        # url = "https://irctc1.p.rapidapi.com/api/v3/getLiveStation"
        url = "https://cttrainsapi.confirmtkt.com/api/v1/trains/search"
        # headers = {
        #     "x-rapidapi-key": settings.RAPIDAPI_KEY,
        #     "x-rapidapi-host": settings.RAPIDAPI_HOST,
        # }
        params = {
            "sourceStationCode": from_station.upper(),
            "destinationStationCode": to_station.upper(),
            "hours": hours,
        }
        
        logger.info(f"Searching trains: {from_station} -> {to_station}")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Process and simplify the response
        trains = data.get("data", {}).get("trainList", [])
        logger.info(f"Found {len(trains)} trains")
        
        processed_trains = []
        for train in trains:
            # Process availability information
            availability_info = {}
            for class_type in train.get("avlClasses", []):
                general_quota = train.get("availabilityCache", {}).get(class_type, {})
                tatkal_quota = train.get("availabilityCacheTatkal", {}).get(class_type, {})
                
                availability_info[class_type] = {
                    "general": {
                        "status": general_quota.get("availability", "NOT AVAILABLE"),
                        "fare": general_quota.get("fare", "0"),
                        "prediction": general_quota.get("prediction", "No prediction"),
                        "prediction_percentage": general_quota.get("predictionPercentage", 0)
                    },
                    "tatkal": {
                        "status": tatkal_quota.get("availability", "NOT AVAILABLE"),
                        "fare": tatkal_quota.get("fare", "0")
                    }
                }
            
            # Create simplified train object
            processed_train = {
                "train_number": train.get("trainNumber"),
                "train_name": train.get("trainName"),
                "from_station": {
                    "code": train.get("fromStnCode"),
                    "name": train.get("fromStnName"),
                    "city": train.get("fromCityName")
                },
                "to_station": {
                    "code": train.get("toStnCode"),
                    "name": train.get("toStnName"),
                    "city": train.get("toCityName")
                },
                "departure": {
                    "time": train.get("departureTime"),
                    "date": train.get("departureDate")
                },
                "arrival": {
                    "time": train.get("arrivalTime")
                },
                "duration_mins": train.get("duration"),
                "distance_km": train.get("distance"),
                "available_classes": train.get("avlClasses", []),
                "availability": availability_info,
                "running_days": train.get("runningDays"),
                "has_pantry": train.get("hasPantry", False),
                "train_rating": train.get("trainRating")
            }
            processed_trains.append(processed_train)
        
        return {
            "success": True,
            "total_trains": len(processed_trains),
            "trains": processed_trains[:15],  # Limit to top 15 for efficiency
            "from_station": from_station.upper(),
            "to_station": to_station.upper()
        }
        
    except Exception as e:
        logger.error(f"Error searching trains: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "trains": []
        }

@tool
def search_station_code(station_name: str) -> Dict[str, Any]:
    """
    Search for station codes by station name. Use this when you have a city/station name but need the code.
    
    Args:
        station_name: Name of the station or city (e.g., 'Mumbai', 'Delhi', 'Bangalore')
    
    Returns:
        Dictionary containing matching stations with their codes
    """
    try:
        url = "https://irctc1.p.rapidapi.com/api/v1/searchStation"
        headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY,
            "x-rapidapi-host": settings.RAPIDAPI_HOST,
        }
        params = {"query": station_name}
        
        logger.info(f"Searching station code for: {station_name}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "stations": data.get("data", [])[:5]  # Top 5 matches
        }
        
    except Exception as e:
        logger.error(f"Error searching station: {str(e)}")
        # Fallback to common station mapping
        return {
            "success": False,
            "error": str(e),
            "stations": []
        }

@tool
def get_station_code_from_city(city_name: str) -> str:
    """
    Get the primary station code for a major Indian city. Use this for quick lookups of common cities.
    
    Args:
        city_name: Name of the city (e.g., 'Delhi', 'Mumbai', 'Bangalore')
    
    Returns:
        Station code as a string (e.g., 'NDLS', 'BCT', 'SBC')
    """
    # Common city to station code mapping
    city_station_map = {
        "delhi": "NDLS",
        "new delhi": "NDLS",
        "yamunanagar": "YJUD",  
        "mumbai": "BCT",
        "bangalore": "SBC",
        "bengaluru": "SBC",
        "chennai": "MAS",
        "hyderabad": "HYB",
        "kolkata": "HWH",
        "pune": "PUNE",
        "ahmedabad": "ADI",
        "jaipur": "JP",
        "lucknow": "LKO",
        "kanpur": "CNB",
        "nagpur": "NGP",
        "indore": "INDB",
        "bhopal": "BPL",
        "patna": "PNBE",
        "agra": "AGC",
        "varanasi": "BSB",
        "surat": "ST",
        "kochi": "ERS",
        "coimbatore": "CBE",
        "guwahati": "GHY",
        "chandigarh": "CDG",
        "thiruvananthapuram": "TVC",
        "vijayawada": "BZA",
        "visakhapatnam": "VSKP",
        "bhubaneswar": "BBS",
        "goa": "MAO",
        "amritsar": "ASR"
    }
    
    city_lower = city_name.lower().strip()
    code = city_station_map.get(city_lower, city_name.upper()[:4])
    logger.info(f"Mapped {city_name} to {code}")
    return code

# Export all tools as a list
railway_tools = [search_trains, search_station_code, get_station_code_from_city]
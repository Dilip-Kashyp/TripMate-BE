import os
import requests
from dotenv import load_dotenv

load_dotenv()

class RailMCP:

    @staticmethod
    def get_live_station(from_station: str, to_station: str, hours: int = 1):
        """Call IRCTC RapidAPI getLiveStation endpoint."""
        url = "https://irctc1.p.rapidapi.com/api/v3/getLiveStation"
        headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv("RAPIDAPI_HOST", "irctc1.p.rapidapi.com"),
        }
        params = {
            "fromStationCode": from_station,
            "toStationCode": to_station,
            "hours": hours,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

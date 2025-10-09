from app.api.v1.routes import live_station  # or via HTTP call
# OR call providers.rail_mcp directly: RailMCP.get_live_station

class AgentManager:
    # existing logic...

    def fetch_live_station(self, from_station: str, to_station: str, hours: int = 1):
        return RailMCP.get_live_station(from_station, to_station, hours)

    def handle_user_query(self, query: str):
        """Decide when to call live_station, etc."""
        # Use your LLM or prompt logic to decide:
        # if user asks “trains from HYD to YRN now” → call fetch_live_station
        # then assemble the response

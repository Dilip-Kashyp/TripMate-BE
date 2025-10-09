from fastapi import APIRouter, Query, HTTPException
from providers.railway.agent import RailMCP

router = APIRouter()

@router.get("/rail/live-station")
def live_station(
    from_station: str = Query(..., alias="from"),
    to_station: str = Query(..., alias="to"),
    hours: int = Query(1),
):
    try:
        data = RailMCP.get_live_station(from_station, to_station, hours)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live station: {str(e)}")

from pydantic import BaseModel, Field

class TravelRequest(BaseModel):
    destination: str = Field(..., min_length=2)
    days: int = Field(..., gt=0)

from pydantic import BaseModel, Field
from typing import Optional


class WeatherQuery(BaseModel):
    lat: float
    lon: float
    stadium_code: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    units: Optional[str] = "imperial"
    lang: Optional[str] = ("en",)
    league: str

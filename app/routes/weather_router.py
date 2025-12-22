from typing import Annotated
from app.auth.auth import AuthUser, RoleChecker
from app.schemas.base import AppBaseResponse
from app.services import weather_service
from app.models.weather_model import WeatherByGroupIdReq
from fastapi import APIRouter, Depends, status


router = APIRouter()

BASE_URL = "/weather"
router = APIRouter(prefix=BASE_URL)


@router.post(
    "/by-group",
    summary="Get weather by group ID",
    description="Get simplified weather type for a location using its group_id. The group_id is used to retrieve the stored latitude and longitude from the database, which are then used to fetch weather data from Google Weather API and map it to simplified weather types.",
    response_description="Simplified weather type: sunny, partly cloudy, cloudy, light rain, or heavy rain",
    status_code=status.HTTP_200_OK,
)
async def get_weather_by_group_id(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get simplified weather type for a location by group_id.
    
    Request Body Parameters:
        - group_id: The unique identifier for the group/store location
    
    Returns simplified weather information:
        - weather_type: One of 5 types
          * "sunny" - Clear/sunny conditions
          * "partly cloudy" - Partially cloudy skies
          * "cloudy" - Overcast/cloudy conditions
          * "light rain" - Light rain or drizzle
          * "heavy rain" - Heavy rain, thunderstorms, or severe weather
        - group_id: The location identifier
        
    All Google Weather API types are mapped to these 5 simplified categories.
    """
    weather = await weather_service.get_weather_by_group_id(data)
    return AppBaseResponse(weather).to_dict()

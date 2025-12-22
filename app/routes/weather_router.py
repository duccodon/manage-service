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


@router.post(
    "/by-group-weatherapi",
    summary="Get weather by group ID using WeatherAPI.com",
    description="Get simplified weather type for a location using its group_id from WeatherAPI.com. This endpoint supports Vietnam and global locations with 1 million free API calls per month. The group_id is used to retrieve the stored latitude and longitude from the database, which are then used to fetch weather data from WeatherAPI.com and map it to simplified weather types.",
    response_description="Simplified weather type: sunny, partly cloudy, cloudy, light rain, or heavy rain",
    status_code=status.HTTP_200_OK,
)
async def get_weather_by_group_id_weatherapi(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get simplified weather type for a location by group_id using WeatherAPI.com.
    
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
        
    All WeatherAPI.com condition codes (40+ types) are mapped to these 5 simplified categories.
    
    Benefits of WeatherAPI.com:
        - Global coverage including Vietnam
        - 1 million free API calls per month
        - Reliable and accurate data
    """
    weather = await weather_service.get_weather_by_group_id_weatherapi(data)
    return AppBaseResponse(weather).to_dict()


@router.post(
    "/hourly-by-group",
    summary="Get 24-hour weather forecast by group ID",
    description="Get 24-hour weather forecast for a location using its group_id from WeatherAPI.com. Returns hourly weather conditions for the current day with simplified weather types and temperature.",
    response_description="24-hour weather forecast with simplified weather types for each hour",
    status_code=status.HTTP_200_OK,
)
async def get_weather_hourly_by_group_id(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get 24-hour weather forecast for a location by group_id using WeatherAPI.com.
    
    Request Body Parameters:
        - group_id: The unique identifier for the group/store location
    
    Returns 24-hour weather forecast:
        - group_id: The location identifier
        - forecast_date: The date of the forecast (YYYY-MM-DD)
        - hourly: Array of 24 hourly weather data, each containing:
          * time: Hour timestamp ("YYYY-MM-DD HH:00")
          * weather_type: One of 5 types (sunny, partly cloudy, cloudy, light rain, heavy rain)
          * temp_c: Temperature in Celsius
    """
    weather = await weather_service.get_weather_hourly_by_group_id(data)
    return AppBaseResponse(weather).to_dict()

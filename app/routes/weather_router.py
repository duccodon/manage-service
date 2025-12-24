from typing import Annotated, Union
from app.auth.auth import AuthUser, RoleChecker
from app.schemas.base import AppBaseResponse
from app.services import weather_service
from app.models.weather_model import WeatherByGroupIdReq, WeatherHistoricalReq
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
    "/hourly-by-group-weatherapi",
    summary="Get 24-hour weather forecast by group ID",
    description="Get 24-hour weather forecast for a location using its group_id from WeatherAPI.com. Returns hourly weather conditions for the current day with simplified weather types and temperature.",
    response_description="24-hour weather forecast with simplified weather types for each hour",
    status_code=status.HTTP_200_OK,
)
async def get_weather_hourly_by_group_id_weatherapi(
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


@router.post(
    "/by-group-openweather",
    summary="Get weather by group ID using OpenWeather API",
    description="Get simplified weather type for a location using its group_id from OpenWeather API. This endpoint provides global coverage with 1,000 free API calls per day. The group_id is used to retrieve the stored latitude and longitude from the database, which are then used to fetch weather data from OpenWeather API and map it to simplified weather types.",
    response_description="Simplified weather type: sunny, partly cloudy, cloudy, light rain, or heavy rain",
    status_code=status.HTTP_200_OK,
)
async def get_weather_by_group_id_openweather(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get simplified weather type for a location by group_id using OpenWeather API.
    
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
        
    All OpenWeather condition codes are mapped to these 5 simplified categories.
    
    Benefits of OpenWeather API:
        - Global coverage
        - 1,000 free API calls per day
        - 60 calls per minute
        - Reliable data source
    """
    weather = await weather_service.get_weather_by_group_id_openweather(data)
    return AppBaseResponse(weather).to_dict()


@router.post(
    "/hourly-by-group-openweather",
    summary="Get 24-hour weather forecast by group ID using OpenWeather API",
    description="Get 24-hour weather forecast for a location using its group_id from OpenWeather API. Returns forecast data in 3-hour intervals for the next 24 hours with simplified weather types and temperature.",
    response_description="24-hour weather forecast with simplified weather types (8 x 3-hour intervals)",
    status_code=status.HTTP_200_OK,
)
async def get_weather_hourly_by_group_id_openweather(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get 24-hour weather forecast for a location by group_id using OpenWeather API.
    
    Request Body Parameters:
        - group_id: The unique identifier for the group/store location
    
    Returns 24-hour weather forecast (8 x 3-hour intervals):
        - group_id: The location identifier
        - forecast_date: The date of the forecast (YYYY-MM-DD)
        - hourly: Array of 8 forecast intervals (3-hour steps), each containing:
          * time: Timestamp ("YYYY-MM-DD HH:00")
          * weather_type: One of 5 types (sunny, partly cloudy, cloudy, light rain, heavy rain)
          * temp_c: Temperature in Celsius
          * chance_of_rain: Probability of precipitation (0-100%)
    """
    weather = await weather_service.get_weather_hourly_by_group_id_openweather(data)
    return AppBaseResponse(weather).to_dict()


@router.post(
    "/by-group-visualcrossing",
    summary="Get weather by group ID using Visual Crossing API (Current or Historical)",
    description="Get simplified weather type for a location using its group_id from Visual Crossing API. Supports both current weather and historical data. This endpoint provides global coverage with 1,000 free records per day. The group_id is used to retrieve the stored latitude and longitude from the database, which are then used to fetch weather data from Visual Crossing API and map it to simplified weather types.",
    response_description="Simplified weather type: sunny, partly cloudy, cloudy, light rain, or heavy rain",
    status_code=status.HTTP_200_OK,
)
async def get_weather_by_group_id_visualcrossing(
    data: WeatherByGroupIdReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get simplified weather type for a location by group_id using Visual Crossing API.
    Supports both current weather and historical data.
    
    Request Body Parameters:
        - group_id: The unique identifier for the group/store location
        - date: (Optional) Date in YYYY-MM-DD format (e.g., "2025-12-24")
                If not provided, returns current weather
                If provided, returns weather for that specific date (historical data)
    
    Returns simplified weather information:
        - weather_type: One of 5 types
          * "sunny" - Clear/sunny conditions
          * "partly cloudy" - Partially cloudy skies
          * "cloudy" - Overcast/cloudy conditions
          * "light rain" - Light rain or drizzle
          * "heavy rain" - Heavy rain, thunderstorms, or severe weather
        - group_id: The location identifier
        
    All Visual Crossing weather icons are mapped to these 5 simplified categories.
    
    Benefits of Visual Crossing API:
        - Global coverage including historical data
        - 1,000 free records per day
        - High accuracy and detailed data
        - Icon-based weather representation
        - Supports historical weather queries
        
    Frontend Usage (React/TypeScript):
        ```typescript
        // Current weather
        const currentWeather = await fetch('/api/v1/weather/by-group-visualcrossing', {
            method: 'POST',
            body: JSON.stringify({ group_id: 'store-123' })
        });
        
        // Historical weather (using Date object)
        const date = new Date('2025-12-20');
        const historicalWeather = await fetch('/api/v1/weather/by-group-visualcrossing', {
            method: 'POST',
            body: JSON.stringify({ 
                group_id: 'store-123',
                date: date.toISOString().split('T')[0] // "2025-12-20"
            })
        });
        ```
    """
    weather = await weather_service.get_weather_by_group_id_visualcrossing(data)
    return AppBaseResponse(weather).to_dict()


@router.post(
    "/hourly-by-group-visualcrossing",
    summary="Get 24-hour weather data by group ID using Visual Crossing API (Current or Historical)",
    description="Get 24-hour weather data for a location using its group_id from Visual Crossing API. Supports both today's forecast and historical hourly data. Returns hourly weather data for the specified day with simplified weather types and temperature.",
    response_description="24-hour weather data with simplified weather types for each hour",
    status_code=status.HTTP_200_OK,
)
async def get_weather_hourly_by_group_id_visualcrossing(
    data: WeatherHistoricalReq,
    #user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Get 24-hour weather data for a location by group_id using Visual Crossing API.
    Supports both today's forecast and historical hourly data.
    
    Request Body Parameters:
        - group_id: The unique identifier for the group/store location
        - date: (Optional) Date in YYYY-MM-DD format (e.g., "2025-12-24")
                If not provided, returns today's hourly forecast
                If provided, returns hourly data for that specific date
    
    Returns 24-hour weather data:
        - group_id: The location identifier
        - forecast_date: The date of the data (YYYY-MM-DD)
        - hourly: Array of 24 hourly weather data, each containing:
          * time: Hour timestamp ("YYYY-MM-DD HH:00")
          * weather_type: One of 5 types (sunny, partly cloudy, cloudy, light rain, heavy rain)
          * temp_c: Temperature in Celsius
          * chance_of_rain: Precipitation probability (0-100%)
          
    Frontend Usage (React/TypeScript):
        ```typescript
        // Today's hourly forecast
        const todayForecast = await fetch('/api/v1/weather/hourly-by-group-visualcrossing', {
            method: 'POST',
            body: JSON.stringify({ group_id: 'store-123' })
        });
        
        // Historical hourly data
        const historicalData = await fetch('/api/v1/weather/hourly-by-group-visualcrossing', {
            method: 'POST',
            body: JSON.stringify({ 
                group_id: 'store-123',
                date: '2025-12-20'
            })
        });
        ```
    """
    weather = await weather_service.get_weather_hourly_by_group_id_visualcrossing(data)
    return AppBaseResponse(weather).to_dict()

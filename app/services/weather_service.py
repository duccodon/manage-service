from app.repositories import weather_repo
from app.models.weather_model import WeatherByGroupIdReq, WeatherResponse
from typing import Optional


async def get_weather_by_group_id(data: WeatherByGroupIdReq) -> Optional[WeatherResponse]:
    """
    Get weather information for a location identified by group_id
    
    Args:
        data: Request containing group_id
        
    Returns:
        WeatherResponse with current weather conditions
        
    Raises:
        Exception: If location not found or weather API fails
    """
    # Fetch weather data using group_id (location lookup happens in repository)
    weather = await weather_repo.get_weather_by_group_id(data.group_id)
    
    return weather


async def get_weather_by_group_id_weatherapi(data: WeatherByGroupIdReq) -> Optional[WeatherResponse]:
    """
    Get weather information for a location identified by group_id using WeatherAPI.com
    
    Args:
        data: Request containing group_id
        
    Returns:
        WeatherResponse with current weather conditions
        
    Raises:
        Exception: If location not found or weather API fails
    """
    # Fetch weather data using group_id from WeatherAPI.com
    weather = await weather_repo.get_weather_by_group_id_weatherapi(data.group_id)
    
    return weather


async def get_weather_hourly_by_group_id(data: WeatherByGroupIdReq):
    """
    Get 24-hour weather forecast for a location identified by group_id using WeatherAPI.com
    
    Args:
        data: Request containing group_id
        
    Returns:
        WeatherHourlyResponse with 24 hours of weather conditions
        
    Raises:
        Exception: If location not found or weather API fails
    """
    # Fetch 24-hour weather forecast using group_id from WeatherAPI.com
    weather = await weather_repo.get_weather_hourly_by_group_id(data.group_id)
    
    return weather

import httpx
from typing import Optional
from app.configs import config
from app.models.weather_model import (
    WeatherResponse,
    WEATHER_TYPE_MAPPING,
    SimplifiedWeatherType,
)
from app.repositories import location_repo
from app.logger.logger import logger


async def get_weather_by_group_id(group_id: str) -> Optional[WeatherResponse]:
    """
    Get current weather conditions from Google Weather API and return simplified weather type
    
    Args:
        group_id: Group/store ID to fetch location and weather data
        
    Returns:
        WeatherResponse with simplified weather type (sunny, partly cloudy, cloudy, light rain, heavy rain)
        
    Raises:
        Exception: If location not found or API call fails
    """
    # Get location from database
    location = await location_repo.get_by_group_id(group_id)
    
    if not location:
        raise Exception(f"Location not found for group_id: {group_id}")
    
    lat = location.lat
    long = location.long
    url = "https://weather.googleapis.com/v1/currentConditions:lookup"
    
    params = {
        "key": config.GOOGLE_MAPS_API_KEY,
        "location.latitude": lat,
        "location.longitude": long,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Weather API response for group_id={group_id}")
            
            # Get weather type from API
            weather_cond = data.get("weatherCondition", {})
            google_weather_type = weather_cond.get("type", "TYPE_UNSPECIFIED")
            
            # Map to simplified weather type
            simplified_type = WEATHER_TYPE_MAPPING.get(
                google_weather_type, SimplifiedWeatherType.CLOUDY
            )
            
            logger.info(
                f"Mapped weather type: {google_weather_type} -> {simplified_type.value}"
            )
            
            # Create simplified response
            weather_response = WeatherResponse(
                weather_type=simplified_type.value,
                group_id=group_id,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Weather API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Weather API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        raise Exception(f"Failed to fetch weather data: {str(e)}")

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


async def get_weather_by_group_id_weatherapi(group_id: str) -> Optional[WeatherResponse]:
    """
    Get current weather conditions from WeatherAPI.com and return simplified weather type
    
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
    url = "http://api.weatherapi.com/v1/current.json"
    
    params = {
        "key": config.WEATHER_API_KEY,
        "q": f"{lat},{long}",
        "aqi": "no",  # Disable air quality data
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"WeatherAPI.com response for group_id={group_id}")
            
            # Get weather condition code from API
            current = data.get("current", {})
            condition = current.get("condition", {})
            weather_code = condition.get("code", 1006)  # Default to cloudy
            
            # Import the mapping
            from app.models.weather_model import WEATHERAPI_CODE_MAPPING
            
            # Map to simplified weather type
            simplified_type = WEATHERAPI_CODE_MAPPING.get(
                weather_code, SimplifiedWeatherType.CLOUDY
            )
            
            logger.info(
                f"Mapped WeatherAPI code: {weather_code} ({condition.get('text')}) -> {simplified_type.value}"
            )
            
            # Create simplified response
            weather_response = WeatherResponse(
                weather_type=simplified_type.value,
                group_id=group_id,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"WeatherAPI.com HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"WeatherAPI.com error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"WeatherAPI.com error: {str(e)}")
        raise Exception(f"Failed to fetch weather data from WeatherAPI.com: {str(e)}")


async def get_weather_hourly_by_group_id(group_id: str):
    """
    Get 24-hour weather forecast from WeatherAPI.com and return simplified weather types
    
    Args:
        group_id: Group/store ID to fetch location and weather data
        
    Returns:
        WeatherHourlyResponse with 24 hours of weather data
        
    Raises:
        Exception: If location not found or API call fails
    """
    # Get location from database
    location = await location_repo.get_by_group_id(group_id)
    
    if not location:
        raise Exception(f"Location not found for group_id: {group_id}")
    
    lat = location.lat
    long = location.long
    url = "http://api.weatherapi.com/v1/forecast.json"
    
    params = {
        "key": config.WEATHER_API_KEY,
        "q": f"{lat},{long}",
        "days": 1,  # Get today's forecast with hourly data
        "aqi": "no",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"WeatherAPI.com hourly forecast for group_id={group_id}")
            
            # Get forecast data
            forecast = data.get("forecast", {})
            forecastday = forecast.get("forecastday", [])
            
            if not forecastday:
                raise Exception("No forecast data available")
            
            today = forecastday[0]
            forecast_date = today.get("date")
            hour_data = today.get("hour", [])
            
            from app.models.weather_model import WEATHERAPI_CODE_MAPPING, HourlyWeather, WeatherHourlyResponse
            
            # Process hourly data
            hourly_weather = []
            for hour in hour_data:
                time = hour.get("time")
                temp_c = hour.get("temp_c", 0.0)
                condition = hour.get("condition", {})
                weather_code = condition.get("code", 1006)
                chance_of_rain = hour.get("chance_of_rain", 0)  
                
                if hour_data.index(hour) == 0:
                    logger.info(f"Sample hour data - chance_of_rain: {chance_of_rain}, condition: {condition.get('text')}")
                
                # Map to simplified weather type
                simplified_type = WEATHERAPI_CODE_MAPPING.get(
                    weather_code, SimplifiedWeatherType.CLOUDY
                )
                
                hourly_weather.append(HourlyWeather(
                    time=time,
                    weather_type=simplified_type.value,
                    temp_c=temp_c,
                    chance_of_rain=chance_of_rain,
                ))
            
            logger.info(f"Processed {len(hourly_weather)} hours of weather data")
            
            # Create response
            weather_response = WeatherHourlyResponse(
                group_id=group_id,
                forecast_date=forecast_date,
                hourly=hourly_weather,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"WeatherAPI.com HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"WeatherAPI.com error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"WeatherAPI.com hourly forecast error: {str(e)}")
        raise Exception(f"Failed to fetch hourly weather data: {str(e)}")

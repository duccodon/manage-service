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

#open weather api, limit free tier
#gg do not support vietnam 
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


# coverage area: 1-11km, 1 million free calls per month, the statistics are not quite correct
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


# OpenWeather API - Free tier: 1,000 calls/day, 60 calls/minute, only have 3h interval forecast for free tier
async def get_weather_by_group_id_openweather(group_id: str) -> Optional[WeatherResponse]:
    """
    Get current weather conditions from OpenWeather API and return simplified weather type
    
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
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": long,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"OpenWeather API response for group_id={group_id}")
            
            # Get weather condition from API
            weather_list = data.get("weather", [])
            if not weather_list:
                raise Exception("No weather data in response")
            
            weather_main = weather_list[0].get("main", "Clouds")
            weather_id = weather_list[0].get("id", 803)
            
            from app.models.weather_model import OPENWEATHER_ID_MAPPING, OPENWEATHER_CONDITION_MAPPING
            
            # Try specific ID mapping first, then fallback to main condition mapping
            simplified_type = OPENWEATHER_ID_MAPPING.get(weather_id)
            if not simplified_type:
                simplified_type = OPENWEATHER_CONDITION_MAPPING.get(
                    weather_main, SimplifiedWeatherType.CLOUDY
                )
            
            logger.info(
                f"Mapped OpenWeather: {weather_main} (ID: {weather_id}) -> {simplified_type.value}"
            )
            
            # Create simplified response
            weather_response = WeatherResponse(
                weather_type=simplified_type.value,
                group_id=group_id,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenWeather API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"OpenWeather API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"OpenWeather API error: {str(e)}")
        raise Exception(f"Failed to fetch weather data from OpenWeather: {str(e)}")


async def get_weather_hourly_by_group_id_openweather(group_id: str):
    """
    Get 24-hour weather forecast from OpenWeather API and return simplified weather types
    
    Args:
        group_id: Group/store ID to fetch location and weather data
        
    Returns:
        WeatherHourlyResponse with hourly weather data
        
    Raises:
        Exception: If location not found or API call fails
    """
    # Get location from database
    location = await location_repo.get_by_group_id(group_id)
    
    if not location:
        raise Exception(f"Location not found for group_id: {group_id}")
    
    lat = location.lat
    long = location.long
    url = "https://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "lat": lat,
        "lon": long,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": 8,  # Get 8 x 3-hour intervals = 24 hours
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"OpenWeather API hourly forecast for group_id={group_id}")
            
            # Get forecast data
            forecast_list = data.get("list", [])
            
            if not forecast_list:
                raise Exception("No forecast data available")
            
            from app.models.weather_model import (
                OPENWEATHER_ID_MAPPING, 
                OPENWEATHER_CONDITION_MAPPING,
                HourlyWeather, 
                WeatherHourlyResponse
            )
            from datetime import datetime
            
            # Process forecast data
            hourly_weather = []
            forecast_date = None
            
            for item in forecast_list:
                dt_txt = item.get("dt_txt")  # Format: "2025-12-24 15:00:00"
                
                # Extract date for response
                if not forecast_date:
                    forecast_date = dt_txt.split(" ")[0]
                
                # Format time to match expected format
                time = dt_txt[:-3]  # Remove seconds: "2025-12-24 15:00"
                
                temp_c = item.get("main", {}).get("temp", 0.0)
                
                # Get weather condition
                weather_list = item.get("weather", [])
                if weather_list:
                    weather_main = weather_list[0].get("main", "Clouds")
                    weather_id = weather_list[0].get("id", 803)
                    
                    # Try specific ID mapping first, then fallback to main condition
                    simplified_type = OPENWEATHER_ID_MAPPING.get(weather_id)
                    if not simplified_type:
                        simplified_type = OPENWEATHER_CONDITION_MAPPING.get(
                            weather_main, SimplifiedWeatherType.CLOUDY
                        )
                else:
                    simplified_type = SimplifiedWeatherType.CLOUDY
                
                # Get chance of rain (pop = probability of precipitation, 0.0-1.0)
                chance_of_rain = item.get("pop", 0) * 100
                
                hourly_weather.append(HourlyWeather(
                    time=time,
                    weather_type=simplified_type.value,
                    temp_c=temp_c,
                    chance_of_rain=chance_of_rain,
                ))
            
            logger.info(f"Processed {len(hourly_weather)} forecast intervals from OpenWeather")
            
            # Create response
            weather_response = WeatherHourlyResponse(
                group_id=group_id,
                forecast_date=forecast_date,
                hourly=hourly_weather,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenWeather API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"OpenWeather API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"OpenWeather API hourly forecast error: {str(e)}")
        raise Exception(f"Failed to fetch hourly weather data from OpenWeather: {str(e)}")


# Visual Crossing API - Free tier: 1,000 records/day, works best
async def get_weather_by_group_id_visualcrossing(group_id: str, date: str = None) -> Optional[WeatherResponse]:
    """
    Get weather conditions from Visual Crossing API for a specific date and return simplified weather type
    
    Args:
        group_id: Group/store ID to fetch location and weather data
        date: Date in YYYY-MM-DD format (e.g., "2025-12-24"). If None, gets current weather
        
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
    
    # Visual Crossing uses location format: "lat,long"
    location_str = f"{lat},{long}"
    
    # Build URL with optional date for historical data
    if date:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_str}/{date}"
        include_param = "days"  # For historical/specific date
    else:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_str}"
        include_param = "current"  # For current weather
    
    params = {
        "key": config.VISUAL_CROSSING_API_KEY,
        "unitGroup": "metric",
        "include": include_param,
        "contentType": "json",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Visual Crossing API response for group_id={group_id}, date={date or 'current'}")
            
            # Get weather conditions (current or from specific date)
            if date:
                # Historical/specific date - get from days array
                days = data.get("days", [])
                if not days:
                    raise Exception(f"No weather data available for date: {date}")
                day_data = days[0]
                icon = day_data.get("icon", "cloudy")
            else:
                # Current weather
                current_conditions = data.get("currentConditions", {})
                if not current_conditions:
                    raise Exception("No current conditions in response")
                icon = current_conditions.get("icon", "cloudy")
            
            from app.models.weather_model import VISUAL_CROSSING_ICON_MAPPING
            
            # Map to simplified weather type
            simplified_type = VISUAL_CROSSING_ICON_MAPPING.get(
                icon, SimplifiedWeatherType.CLOUDY
            )
            
            logger.info(
                f"Mapped Visual Crossing icon: {icon} -> {simplified_type.value}"
            )
            
            # Create simplified response
            weather_response = WeatherResponse(
                weather_type=simplified_type.value,
                group_id=group_id,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Visual Crossing API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Visual Crossing API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Visual Crossing API error: {str(e)}")
        raise Exception(f"Failed to fetch weather data from Visual Crossing: {str(e)}")


async def get_weather_hourly_by_group_id_visualcrossing(group_id: str, date: str = None):
    """
    Get 24-hour weather data from Visual Crossing API for a specific date and return simplified weather types
    
    Args:
        group_id: Group/store ID to fetch location and weather data
        date: Date in YYYY-MM-DD format (e.g., "2025-12-24"). If None, gets today's forecast
        
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
    
    # Visual Crossing uses location format: "lat,long"
    location_str = f"{lat},{long}"
    
    # Build URL with date (default to today if not specified)
    date_param = date if date else "today"
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_str}/{date_param}"
    
    params = {
        "key": config.VISUAL_CROSSING_API_KEY,
        "unitGroup": "metric",
        "include": "hours",
        "contentType": "json",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Visual Crossing API hourly forecast for group_id={group_id}")
            
            # Get forecast data
            days = data.get("days", [])
            
            if not days:
                raise Exception("No forecast data available")
            
            today = days[0]
            forecast_date = today.get("datetime")  # Format: "2025-12-24"
            hours = today.get("hours", [])
            
            from app.models.weather_model import VISUAL_CROSSING_ICON_MAPPING, HourlyWeather, WeatherHourlyResponse
            
            # Process hourly data
            hourly_weather = []
            for hour in hours:
                datetime_str = hour.get("datetime")  # Format: "15:00:00"
                hour_time = datetime_str[:5]  # Extract "15:00"
                time = f"{forecast_date} {hour_time}"  # "2025-12-24 15:00"
                
                temp_c = hour.get("temp", 0.0)
                icon = hour.get("icon", "cloudy")
                precip_prob = hour.get("precipprob", 0)  # Precipitation probability 0-100
                
                # Map to simplified weather type
                simplified_type = VISUAL_CROSSING_ICON_MAPPING.get(
                    icon, SimplifiedWeatherType.CLOUDY
                )
                
                hourly_weather.append(HourlyWeather(
                    time=time,
                    weather_type=simplified_type.value,
                    temp_c=temp_c,
                    chance_of_rain=precip_prob,
                ))
            
            logger.info(f"Processed {len(hourly_weather)} hours from Visual Crossing")
            
            # Create response
            weather_response = WeatherHourlyResponse(
                group_id=group_id,
                forecast_date=forecast_date,
                hourly=hourly_weather,
            )
            
            return weather_response
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Visual Crossing API HTTP error: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Visual Crossing API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Visual Crossing API hourly forecast error: {str(e)}")
        raise Exception(f"Failed to fetch hourly weather data from Visual Crossing: {str(e)}")

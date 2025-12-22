from enum import Enum
from pydantic import BaseModel


class SimplifiedWeatherType(str, Enum):
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly cloudy"
    CLOUDY = "cloudy"
    LIGHT_RAIN = "light rain"
    HEAVY_RAIN = "heavy rain"

WEATHER_TYPE_MAPPING = {
    # Sunny/Clear conditions
    "CLEAR": SimplifiedWeatherType.SUNNY,
    "MOSTLY_CLEAR": SimplifiedWeatherType.SUNNY,
    
    # Partly cloudy
    "PARTLY_CLOUDY": SimplifiedWeatherType.PARTLY_CLOUDY,
    
    # Cloudy
    "MOSTLY_CLOUDY": SimplifiedWeatherType.CLOUDY,
    "CLOUDY": SimplifiedWeatherType.CLOUDY,
    "WINDY": SimplifiedWeatherType.CLOUDY,
    
    # Light rain
    "LIGHT_RAIN": SimplifiedWeatherType.LIGHT_RAIN,
    "LIGHT_RAIN_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "CHANCE_OF_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "SCATTERED_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "LIGHT_TO_MODERATE_RAIN": SimplifiedWeatherType.LIGHT_RAIN,
    
    # Heavy rain
    "RAIN": SimplifiedWeatherType.HEAVY_RAIN,
    "RAIN_SHOWERS": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_RAIN_SHOWERS": SimplifiedWeatherType.HEAVY_RAIN,
    "MODERATE_TO_HEAVY_RAIN": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_RAIN": SimplifiedWeatherType.HEAVY_RAIN,
    "RAIN_PERIODICALLY_HEAVY": SimplifiedWeatherType.HEAVY_RAIN,
    "WIND_AND_RAIN": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Thunderstorms → Heavy rain
    "THUNDERSTORM": SimplifiedWeatherType.HEAVY_RAIN,
    "THUNDERSHOWER": SimplifiedWeatherType.HEAVY_RAIN,
    "LIGHT_THUNDERSTORM_RAIN": SimplifiedWeatherType.HEAVY_RAIN,
    "SCATTERED_THUNDERSTORMS": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_THUNDERSTORM": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Snow → Treated as heavy rain for simplicity
    "LIGHT_SNOW": SimplifiedWeatherType.LIGHT_RAIN,
    "LIGHT_SNOW_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "CHANCE_OF_SNOW_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "SCATTERED_SNOW_SHOWERS": SimplifiedWeatherType.LIGHT_RAIN,
    "LIGHT_TO_MODERATE_SNOW": SimplifiedWeatherType.LIGHT_RAIN,
    "SNOW": SimplifiedWeatherType.HEAVY_RAIN,
    "SNOW_SHOWERS": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_SNOW_SHOWERS": SimplifiedWeatherType.HEAVY_RAIN,
    "MODERATE_TO_HEAVY_SNOW": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_SNOW": SimplifiedWeatherType.HEAVY_RAIN,
    "SNOWSTORM": SimplifiedWeatherType.HEAVY_RAIN,
    "SNOW_PERIODICALLY_HEAVY": SimplifiedWeatherType.HEAVY_RAIN,
    "HEAVY_SNOW_STORM": SimplifiedWeatherType.HEAVY_RAIN,
    "BLOWING_SNOW": SimplifiedWeatherType.HEAVY_RAIN,
    "RAIN_AND_SNOW": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Hail → Heavy rain
    "HAIL": SimplifiedWeatherType.HEAVY_RAIN,
    "HAIL_SHOWERS": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Default fallback
    "TYPE_UNSPECIFIED": SimplifiedWeatherType.CLOUDY,
}


class WeatherResponse(BaseModel):
    """Simplified weather response"""
    weather_type: str  # One of: sunny, partly cloudy, cloudy, light rain, heavy rain
    group_id: str


class WeatherByGroupIdReq(BaseModel):
    """Request model for getting weather by group_id"""
    group_id: str

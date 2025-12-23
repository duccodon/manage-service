from enum import Enum
from typing import Optional
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

# WeatherAPI.com condition code mapping (code to simplified type)
WEATHERAPI_CODE_MAPPING = {
    # Sunny/Clear - Code 1000
    1000: SimplifiedWeatherType.SUNNY,
    
    # Partly cloudy - Code 1003
    1003: SimplifiedWeatherType.PARTLY_CLOUDY,
    
    # Cloudy - Codes 1006, 1009
    1006: SimplifiedWeatherType.CLOUDY,
    1009: SimplifiedWeatherType.CLOUDY,  # Overcast
    
    # Cloudy (Mist/Fog treated as cloudy)
    1030: SimplifiedWeatherType.CLOUDY,  # Mist
    1135: SimplifiedWeatherType.CLOUDY,  # Fog
    1147: SimplifiedWeatherType.CLOUDY,  # Freezing fog
    
    # Light rain - Codes 1063, 1150, 1153, 1168, 1180, 1183, 1198, 1240
    1063: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy rain possible
    1150: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy light drizzle
    1153: SimplifiedWeatherType.LIGHT_RAIN,  # Light drizzle
    1168: SimplifiedWeatherType.LIGHT_RAIN,  # Freezing drizzle
    1180: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy light rain
    1183: SimplifiedWeatherType.LIGHT_RAIN,  # Light rain
    1198: SimplifiedWeatherType.LIGHT_RAIN,  # Light freezing rain
    1240: SimplifiedWeatherType.LIGHT_RAIN,  # Light rain shower
    
    # Heavy rain - Codes 1186, 1189, 1192, 1195, 1201, 1243, 1246
    1186: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate rain at times
    1189: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate rain
    1192: SimplifiedWeatherType.HEAVY_RAIN,  # Heavy rain at times
    1195: SimplifiedWeatherType.HEAVY_RAIN,  # Heavy rain
    1201: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy freezing rain
    1243: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy rain shower
    1246: SimplifiedWeatherType.HEAVY_RAIN,  # Torrential rain shower
    
    # Thunderstorms -> Heavy rain - Codes 1087, 1273, 1276
    1087: SimplifiedWeatherType.HEAVY_RAIN,  # Thundery outbreaks possible
    1273: SimplifiedWeatherType.HEAVY_RAIN,  # Patchy light rain with thunder
    1276: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy rain with thunder
    
    # Snow -> Light rain for light snow, Heavy rain for heavy snow
    1066: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy snow possible
    1210: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy light snow
    1213: SimplifiedWeatherType.LIGHT_RAIN,  # Light snow
    1255: SimplifiedWeatherType.LIGHT_RAIN,  # Light snow showers
    1216: SimplifiedWeatherType.HEAVY_RAIN,  # Patchy moderate snow
    1219: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate snow
    1222: SimplifiedWeatherType.HEAVY_RAIN,  # Patchy heavy snow
    1225: SimplifiedWeatherType.HEAVY_RAIN,  # Heavy snow
    1258: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy snow showers
    1114: SimplifiedWeatherType.HEAVY_RAIN,  # Blowing snow
    1117: SimplifiedWeatherType.HEAVY_RAIN,  # Blizzard
    1279: SimplifiedWeatherType.HEAVY_RAIN,  # Patchy light snow with thunder
    1282: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy snow with thunder
    
    # Sleet -> Heavy rain
    1069: SimplifiedWeatherType.HEAVY_RAIN,  # Patchy sleet possible
    1072: SimplifiedWeatherType.LIGHT_RAIN,  # Patchy freezing drizzle possible
    1204: SimplifiedWeatherType.HEAVY_RAIN,  # Light sleet
    1207: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy sleet
    1249: SimplifiedWeatherType.HEAVY_RAIN,  # Light sleet showers
    1252: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy sleet showers
    
    # Ice pellets -> Heavy rain
    1237: SimplifiedWeatherType.HEAVY_RAIN,  # Ice pellets
    1261: SimplifiedWeatherType.HEAVY_RAIN,  # Light showers of ice pellets
    1264: SimplifiedWeatherType.HEAVY_RAIN,  # Moderate or heavy showers of ice pellets
}

# OpenWeather condition code mapping (main weather condition to simplified type)
OPENWEATHER_CONDITION_MAPPING = {
    # Clear - id 800
    "Clear": SimplifiedWeatherType.SUNNY,
    
    # Clouds - ids 801-804
    "Clouds": SimplifiedWeatherType.CLOUDY,  # Default for all cloud types
    
    # Drizzle - ids 300-321 (light rain)
    "Drizzle": SimplifiedWeatherType.LIGHT_RAIN,
    
    # Rain - ids 500-531
    "Rain": SimplifiedWeatherType.HEAVY_RAIN,  # Default for rain
    
    # Thunderstorm - ids 200-232
    "Thunderstorm": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Snow - ids 600-622
    "Snow": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Atmosphere (mist, fog, etc) - ids 701-781
    "Mist": SimplifiedWeatherType.CLOUDY,
    "Smoke": SimplifiedWeatherType.CLOUDY,
    "Haze": SimplifiedWeatherType.CLOUDY,
    "Dust": SimplifiedWeatherType.CLOUDY,
    "Fog": SimplifiedWeatherType.CLOUDY,
    "Sand": SimplifiedWeatherType.CLOUDY,
    "Ash": SimplifiedWeatherType.CLOUDY,
    "Squall": SimplifiedWeatherType.HEAVY_RAIN,
    "Tornado": SimplifiedWeatherType.HEAVY_RAIN,
}

# OpenWeather detailed ID mapping for more accurate classification
OPENWEATHER_ID_MAPPING = {
    # Clear
    800: SimplifiedWeatherType.SUNNY,
    
    # Clouds
    801: SimplifiedWeatherType.PARTLY_CLOUDY,  # Few clouds: 11-25%
    802: SimplifiedWeatherType.PARTLY_CLOUDY,  # Scattered clouds: 25-50%
    803: SimplifiedWeatherType.CLOUDY,  # Broken clouds: 51-84%
    804: SimplifiedWeatherType.CLOUDY,  # Overcast clouds: 85-100%
    
    # Light rain (500-504, 520)
    500: SimplifiedWeatherType.LIGHT_RAIN,  # Light rain
    501: SimplifiedWeatherType.LIGHT_RAIN,  # Moderate rain
    520: SimplifiedWeatherType.LIGHT_RAIN,  # Light intensity shower rain
}

# Visual Crossing icon mapping to simplified type
VISUAL_CROSSING_ICON_MAPPING = {
    # Clear/Sunny
    "clear-day": SimplifiedWeatherType.SUNNY,
    "clear-night": SimplifiedWeatherType.SUNNY,
    
    # Partly cloudy
    "partly-cloudy-day": SimplifiedWeatherType.PARTLY_CLOUDY,
    "partly-cloudy-night": SimplifiedWeatherType.PARTLY_CLOUDY,
    
    # Cloudy
    "cloudy": SimplifiedWeatherType.CLOUDY,
    "wind": SimplifiedWeatherType.CLOUDY,
    "fog": SimplifiedWeatherType.CLOUDY,
    
    # Light rain
    "showers-day": SimplifiedWeatherType.LIGHT_RAIN,
    "showers-night": SimplifiedWeatherType.LIGHT_RAIN,
    
    # Heavy rain
    "rain": SimplifiedWeatherType.HEAVY_RAIN,
    "thunder-rain": SimplifiedWeatherType.HEAVY_RAIN,
    "thunder-showers-day": SimplifiedWeatherType.HEAVY_RAIN,
    "thunder-showers-night": SimplifiedWeatherType.HEAVY_RAIN,
    
    # Snow -> Heavy rain
    "snow": SimplifiedWeatherType.HEAVY_RAIN,
    "snow-showers-day": SimplifiedWeatherType.HEAVY_RAIN,
    "snow-showers-night": SimplifiedWeatherType.HEAVY_RAIN,
    "hail": SimplifiedWeatherType.HEAVY_RAIN,
}


class WeatherResponse(BaseModel):
    """Simplified weather response"""
    weather_type: str  # One of: sunny, partly cloudy, cloudy, light rain, heavy rain
    group_id: str


class HourlyWeather(BaseModel):
    """Hourly weather data"""
    time: str  # Format: "2025-12-22 14:00"
    weather_type: str  # One of: sunny, partly cloudy, cloudy, light rain, heavy rain
    temp_c: float
    chance_of_rain: float = 0.0 


class WeatherHourlyResponse(BaseModel):
    """24-hour weather forecast response"""
    group_id: str
    forecast_date: str  # Format: "2025-12-22"
    hourly: list[HourlyWeather]  


class WeatherByGroupIdReq(BaseModel):
    """Request model for getting weather by group_id"""
    group_id: str


class WeatherHistoricalReq(BaseModel):
    """Request model for getting historical weather by group_id and date"""
    group_id: str
    date: Optional[str] = None  # Format: YYYY-MM-DD (e.g., "2025-12-24"). If None, uses current date

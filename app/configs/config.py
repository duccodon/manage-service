import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", default="DEV")
PORT = os.getenv("PORT", default="8000")

# SECRET KEY
SECRET_KEY = os.getenv("SECRET_KEY")

# MONGODB
MONGO_URI = os.getenv("MONGO_URI")
MONGODB_NAME = os.getenv("MONGODB_NAME")


# Mongo collections
LOCATION_COLLECTION = os.getenv("LOCATION_COLLECTION")
NOTIFICATION_COLLECTION = os.getenv("NOTIFICATION_COLLECTION")

# Google Maps API
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# WeatherAPI.com
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# OpenWeather API
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Visual Crossing API
VISUAL_CROSSING_API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
import googlemaps
from app.configs import config
from app.repositories import location_repo
from app.models.location_model import LocationCreateReq


# Initialize Google Maps client
gmaps = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)


async def geocode_address(address: str) -> tuple[float, float]:
    """
    Convert address to latitude and longitude using Google Maps Geocoding API
    
    Returns:
        tuple: (latitude, longitude)
    
    Raises:
        Exception: If geocoding fails or no results found
    """
    try:
        geocode_result = gmaps.geocode(address)
        
        if not geocode_result:
            raise Exception(f"No geocoding results found for address: {address}")
        
        location = geocode_result[0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']
        
        return lat, lng
    except Exception as e:
        raise Exception(f"Geocoding error: {str(e)}")


async def create_location(data: LocationCreateReq) -> dict:
    """
    Create a new location by geocoding the address
    """
    lat, lng = await geocode_address(data.address)
    
    # Save to database
    location = await location_repo.create_location(
        group_id=data.group_id,
        address=data.address,
        lat=lat,
        long=lng
    )
    
    return location

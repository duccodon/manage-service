from app.db.database import location_collection
from app.models.location_model import Location


async def create_location(group_id: str, address: str, lat: float, long: float) -> dict:
    """
    Create a new location record using group_id as primary key
    """
    
    location_data = {
        "_id": group_id,
        "address": address,
        "lat": lat,
        "long": long,
    }
    
    await location_collection.insert_one(location_data)
    
    return Location.model_validate(location_data)


async def get_by_group_id(group_id: str) -> dict | None:
    """
    Get location by group_id (which is the _id)
    """
    doc = await location_collection.find_one({"_id": group_id})
    if doc:
        return Location.model_validate(doc)
    return None

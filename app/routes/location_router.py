from typing import Annotated
from app.auth.auth import AuthUser, RoleChecker
from app.schemas.base import AppBaseResponse
from app.services import location_service
from app.models.location_model import LocationCreateReq
from fastapi import APIRouter, Depends, status


router = APIRouter()

BASE_URL = "/locations"
router = APIRouter(prefix=BASE_URL)


@router.post(
    "",
    summary="Create a new geocoding",
    description="Create a new location by geocoding an address using Google Maps API. The address will be converted to latitude and longitude coordinates.",
    response_description="Successfully created location with geocoded coordinates",
    status_code=status.HTTP_200_OK,
)
async def create_location(
    data: LocationCreateReq,
    # user: Annotated[AuthUser, Depends(RoleChecker())],
):
    """
    Create a new location by geocoding an address.
    
    Request Body Parameters:
        - group_id: Unique identifier for the group/store (used as primary key)
        - address: Full address like in Google Maps to be geocoded 
        (e.g., "485B Nguyễn Đình Chiểu, Phường 2, Quận 3, Thành phố Hồ Chí Minh 700000, Vietnam")
    
    Returns the created location with latitude and longitude coordinates.
    """
    location = await location_service.create_location(data)
    return AppBaseResponse(location).to_dict()

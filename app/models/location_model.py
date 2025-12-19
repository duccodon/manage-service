from typing import Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    group_id: str = Field(..., alias="_id")
    address: str
    lat: float
    long: float

    class Config:
        populate_by_name = True


class LocationCreateReq(BaseModel):
    group_id: str
    address: str


class LocationRes(BaseModel):
    group_id: str
    address: str
    lat: float
    long: float

from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime
from bson import Binary, UUID_SUBTYPE


class NotificationStatus(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class NotificationType(str, Enum):
    product_zone_overcrowded = "product_zone_overcrowded"
    checkout_delay = "checkout_delay"
    long_queue_detected = "long_queue_detected"
    unattended_items_detected = "unattended_items_detected"
    smoke_fire_detected = "smoke_fire_etected"
    traffic_insight = "traffic_insight"

    # Thông báo chung
    info = "info"
    undefine = "undefine"


class Notification(BaseModel):
    id: str = Field(..., alias="_id")  # bytes
    title: Optional[str] = None
    description: Optional[str] = None

    data: Dict[str, Any]

    status: NotificationStatus
    type: NotificationType

    users_read: List[str] = Field(default_factory=list)
    users_delete: List[str] = Field(default_factory=list)

    has_for_all: bool

    tenant_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)
    store_ids: List[str] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    def convert_bson_uuid(cls, v):
        """
        Convert MongoDB Binary(UUID) -> string UUID
        """
        if isinstance(v, Binary) and v.subtype == UUID_SUBTYPE:
            return str(uuid.UUID(bytes=v))
        if isinstance(v, (bytes, bytearray)):  # fallback
            return str(uuid.UUID(bytes=v))
        return v

    class Config:
        populate_by_name = True  # Cho phép parse theo _id
        arbitrary_types_allowed = True


class NotificationData(BaseModel):
    cam_id: str = Field(...)
    zone_id: str = Field(...)

    image: Optional[str] = None
    duration_second: Optional[int] = None
    people_count: Optional[int] = None
    avg_dwell_time: Optional[int] = None

    class Config:
        populate_by_name = True


class NotificationRes(BaseModel):
    id: str = Field(..., alias="_id")
    title: Optional[str] = None
    description: Optional[str] = None
    # data: Dict[str, Any]
    status: NotificationStatus
    type: NotificationType
    created_at: datetime
    is_read: bool

    @field_validator("id", mode="before")
    def convert_bson_uuid(cls, v):
        """
        Convert MongoDB Binary(UUID) -> string UUID
        """
        if isinstance(v, Binary) and v.subtype == UUID_SUBTYPE:
            return str(uuid.UUID(bytes=v))
        if isinstance(v, (bytes, bytearray)):  # fallback
            return str(uuid.UUID(bytes=v))
        return v

    class Config:
        populate_by_name = True  # Cho phép parse theo _id
        arbitrary_types_allowed = True


def to_notification_res(data: dict, user_id: str) -> dict:
    is_read = user_id in data.get("users_read")

    record = NotificationRes(
        id=data.get("_id"),
        title=data.get("title"),
        description=data.get("description"),
        # data=data.get("data"),
        status=data.get("status"),
        type=data.get("type"),
        is_read=is_read,
        created_at=data.get("created_at"),
    )

    return record.dict()

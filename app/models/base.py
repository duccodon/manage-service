from enum import Enum


class ObjectStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    IS_DELETED = "delete"

from app.repositories import notification_repo
from app.schemas.base import BasePagingReq


async def get_by_id(id_str: str) -> dict | None:
    return await notification_repo.get_by_id(id_str)


async def get_by_filter(params: BasePagingReq, tenant_id: str, user_id: str) -> dict:
    return await notification_repo.get_by_filter(params, tenant_id, user_id)

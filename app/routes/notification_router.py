from typing import Annotated, Optional
from app.auth.auth import AuthUser, RoleChecker
from app.schemas.base import AppBaseResponse, BasePagingReq
from app.services import notification_service
from fastapi import APIRouter, Depends


router = APIRouter()

BASE_URL = "/notifications"
router = APIRouter(prefix=BASE_URL)


@router.get("/{id}")
async def get_by_id(id: str):
    noti = await notification_service.get_by_id(id)

    return AppBaseResponse(noti).to_dict()


@router.get("")
async def get_by_filter(
    user: Annotated[AuthUser, Depends(RoleChecker())],
    keyword: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = 10,
):
    noti = await notification_service.get_by_filter(
        BasePagingReq(keyword=keyword, page=page, page_size=page_size),
        user.user_id,
        user.user_id,
    )

    return AppBaseResponse(noti).to_dict()

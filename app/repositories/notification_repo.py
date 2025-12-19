import re
import uuid
from app.db.database import notification_collection
from app.models.base import ObjectStatus
from app.models.notification_model import Notification, to_notification_res
from app.schemas.base import AppBasePagingRes, BasePagingReq
from bson import Binary, UUID_SUBTYPE


async def get_by_id(id_str: str) -> dict | None:
    uid = uuid.UUID(id_str)
    bson_id = Binary(uid.bytes, UUID_SUBTYPE)

    doc = await notification_collection.find_one({"_id": bson_id})
    if doc:
        return Notification.model_validate(doc)
    return None


async def get_by_filter(params: BasePagingReq, tenant_id: str, user_id: str):
    # nếu None thì return giá trị này
    empty_items = AppBasePagingRes(
        items=[],
        page_size=params.page_size,
        page=params.page,
        total=0,
        is_full=True,
    ).to_dict()
    query = {
        # bỏ qua các thông báo mà user đã xoá theo users_delete
        "users_delete": {"$ne": user_id},
        "$or": [
            # 1. Notification dành cho tất cả
            {"has_for_all": True},
            # 2. Notification không dành cho tất cả
            {
                "has_for_all": False,
                # user_id == user_id hoặc user_id không tồn tại
                "$or": [
                    {"user_id": user_id},
                    {"user_id": None},
                ],
                # tenant_id phải match nếu có
                "tenant_id": tenant_id,
            },
        ],
    }

    # TODO
    # lọc theo store_ids mà user được access (nếu có)
    # store_ids = get_store_ids
    # if store_ids:
    #     query["$or"].append({"store_ids": {"$in": params.store_ids}})

    # tìm theo title
    if params.keyword:
        keyword_regex = re.compile(f".*{params.keyword}.*", re.IGNORECASE)
        query.update(
            {
                {"title": {"$regex": keyword_regex}},
            }
        )

    skip = (params.page - 1) * params.page_size

    # lấy total
    total = await notification_collection.count_documents(query)

    records = (
        await notification_collection.find(query)
        .skip(skip)
        .limit(params.page_size)
        .to_list()
    )

    if not records or len(records) == 0:
        return empty_items

    res_data = list(map(lambda x: to_notification_res(x, user_id), records))
    return AppBasePagingRes(
        items=res_data,
        page_size=params.page_size,
        page=params.page,
        total=total,
        is_full=params.page_size * params.page >= total,
    ).to_dict()

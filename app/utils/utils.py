from datetime import datetime
from zoneinfo import ZoneInfo
import pytz
from app.constants.constant import LOCAL_TIMEZONE
from io import BytesIO


vn_timezone = ZoneInfo(LOCAL_TIMEZONE)
utc_timezone = pytz.UTC


def reduce(func, iterable, initializer=None):
    it = iter(iterable)

    # Nếu không có initializer, lấy phần tử đầu tiên của iterable làm accumulator
    if initializer is None:
        accumulator = next(it)
    else:
        accumulator = initializer

    for item in it:
        accumulator = func(accumulator, item)

    return accumulator


def convert_timestamp_to_iso(timestamp: float) -> str:
    """Chuyển timestamp epoch thành chuỗi định dạng ISO 8601 (2025-05-28T15:46:13.147Z)."""
    if timestamp is None:
        return None
    dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    return dt.isoformat().replace("+00:00", "Z")  # Định dạng ISO 8601 với 'Z'

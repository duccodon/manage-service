# Copilot Instructions for manage-service

## Project Overview
FastAPI microservice for managing notifications and weather data in the cxview system. Uses MongoDB with Motor (async driver), JWT authentication, Google Weather API integration, and a layered architecture (router → service → repository).

## Architecture & Patterns

### Layered Architecture (Strict Flow)
- **Router** (`app/routes/`) → **Service** (`app/services/`) → **Repository** (`app/repositories/`)
- Example: [notification_router.py](../app/routes/notification_router.py) calls [notification_service.py](../app/services/notification_service.py) which calls [notification_repo.py](../app/repositories/notification_repo.py)
- **Never** skip layers - routers should not directly call repositories

### MongoDB UUID Handling
UUIDs are stored as Binary(UUID_SUBTYPE), not strings. Pattern from [notification_repo.py](../app/repositories/notification_repo.py#L10-L14):
```python
import uuid
from bson import Binary, UUID_SUBTYPE

uid = uuid.UUID(id_str)
bson_id = Binary(uid.bytes, UUID_SUBTYPE)
doc = await collection.find_one({"_id": bson_id})
```

Models use field validators to convert Binary → string UUID. See [notification_model.py](../app/models/notification_model.py#L52-L61).

### Response Wrapping
All endpoints return standardized responses using [base.py](../app/schemas/base.py) schemas:
- **Success**: `AppBaseResponse(data).to_dict()` or `.to_json()`
- **Pagination**: `AppBasePagingRes(items, page, page_size, total, is_full).to_dict()`
- **Errors**: Handled globally via exception handlers in [main.py](../app/main.py#L76-L100)

### Authentication & Authorization
JWT-based auth via [auth.py](../app/auth/auth.py):
```python
from app.auth.auth import AuthUser, RoleChecker

@router.get("")
async def endpoint(user: Annotated[AuthUser, Depends(RoleChecker())]):
    # user.user_id, user.role, user.email available
```
- `RoleChecker()` with no args → any authenticated user
- `RoleChecker(["admin"])` → specific roles only
- Token passed in `Authorization` header (not Bearer prefix in current implementation)

### Multi-Tenancy Pattern
Notification queries implement soft multi-tenancy in [notification_repo.py](../app/repositories/notification_repo.py#L22-L45):
- Filter by `tenant_id` and `user_id` 
- Support `has_for_all` flag for broadcast notifications
- Implement soft delete via `users_delete` array (not hard deletes)

## Weather API Integration

### Overview
Weather feature provides simplified weather conditions using **WeatherAPI.com** (primary) and Google Weather API (limited coverage). All weather conditions from APIs (40+ types) are mapped to 5 simplified categories for frontend consistency. See [weather_model.py](../app/models/weather_model.py) and [weather_repo.py](../app/repositories/weather_repo.py).

### Simplified Weather Types
All weather APIs return one of 5 standardized types:
- **"sunny"** - Clear/sunny conditions
- **"partly cloudy"** - Partially cloudy skies  
- **"cloudy"** - Overcast/cloudy conditions
- **"light rain"** - Light rain or drizzle
- **"heavy rain"** - Heavy rain, thunderstorms, or severe weather

### Request Model ([weather_model.py](../app/models/weather_model.py))
```python
class WeatherByGroupIdReq(BaseModel):
    group_id: str  # Used to fetch lat/long from location collection
```

### Response Models

#### Current Weather Response
```python
class WeatherResponse(BaseModel):
    weather_type: str  # One of 5 simplified types
    group_id: str
```

#### Hourly Forecast Response (24 hours)
```python
class HourlyWeather(BaseModel):
    time: str  # Format: "2025-12-22 14:00"
    weather_type: str  # One of 5 simplified types
    temp_c: float  # Temperature in Celsius

class WeatherHourlyResponse(BaseModel):
    group_id: str
    forecast_date: str  # Format: "2025-12-22"
    hourly: list[HourlyWeather]  # 24 hours of data
```

### Available Endpoints

#### 1. Current Weather - WeatherAPI.com (Recommended)
**POST /api/v1/weather/by-group-weatherapi**
- **Coverage**: Global including Vietnam 🇻🇳
- **API Limit**: 1 million calls/month (free tier)
- **Returns**: Current weather type and group_id

```python
# Request:
{"group_id": "store-123"}

# Response:
{
  "data": {
    "weather_type": "partly cloudy",
    "group_id": "store-123"
  }
}
```

#### 2. 24-Hour Forecast - WeatherAPI.com
**POST /api/v1/weather/hourly-by-group**
- **Coverage**: Global including Vietnam 🇻🇳
- **Returns**: Hourly weather for current day (24 hours)

```python
# Request:
{"group_id": "store-123"}

# Response:
{
  "data": {
    "group_id": "store-123",
    "forecast_date": "2025-12-22",
    "hourly": [
      {"time": "2025-12-22 00:00", "weather_type": "cloudy", "temp_c": 27.5},
      {"time": "2025-12-22 01:00", "weather_type": "partly cloudy", "temp_c": 27.0},
      // ... 22 more hours
    ]
  }
}
```

#### 3. Current Weather - Google Weather API (Legacy)
**POST /api/v1/weather/by-group**
- **Coverage**: Limited (excludes Vietnam and many regions)
- **Returns**: Current weather type and group_id
- **Note**: Returns 404 for unsupported regions

### Weather Type Mapping

#### WeatherAPI.com Code Mapping (`WEATHERAPI_CODE_MAPPING`)
Maps condition codes to simplified types:
- **sunny** ← Code 1000 (Sunny/Clear)
- **partly cloudy** ← Code 1003 (Partly cloudy)
- **cloudy** ← Codes 1006, 1009, 1030, 1135, 1147 (Cloudy, Overcast, Mist, Fog)
- **light rain** ← Codes 1063, 1150, 1153, 1180, 1183, 1240, etc. (Light rain variants)
- **heavy rain** ← Codes 1186, 1189, 1195, 1243, 1246, 1087, 1273, 1276, etc. (Heavy rain, thunderstorms)
- Snow conditions mapped to rain equivalents (light snow → light rain, heavy snow → heavy rain)

#### Google Weather API Mapping (`WEATHER_TYPE_MAPPING`)
Maps text types to simplified types:
- **sunny** ← `CLEAR`, `MOSTLY_CLEAR`
- **partly cloudy** ← `PARTLY_CLOUDY`
- **cloudy** ← `CLOUDY`, `MOSTLY_CLOUDY`, `WINDY`
- **light rain** ← `LIGHT_RAIN`, `LIGHT_RAIN_SHOWERS`, `SCATTERED_SHOWERS`, etc.
- **heavy rain** ← `RAIN`, `HEAVY_RAIN`, `THUNDERSTORM`, `SNOW`, `HAIL`, etc.

### Implementation Architecture

#### Repository Layer Flow
1. Client sends `group_id` in request body
2. Repository calls `location_repo.get_by_group_id()` to fetch coordinates
3. Makes async HTTP request to weather API using `httpx.AsyncClient()`
4. Receives raw weather data with condition code/type
5. Maps to simplified weather type using appropriate mapping dictionary
6. Returns standardized response model

#### Key Implementation Details
- **APIs**: WeatherAPI.com (primary), Google Weather API (fallback)
- **API Keys**: `WEATHER_API_KEY` (WeatherAPI.com), `GOOGLE_MAPS_API_KEY` in `.env`
- **HTTP Client**: `httpx.AsyncClient()` for async requests
- **Authentication**: All endpoints require `RoleChecker()` (JWT auth)
- **Error Handling**: Location not found, API failures, unsupported regions
- **Logging**: Detailed logs for API calls and mapping results

#### Repository Functions
- `get_weather_by_group_id_weatherapi()` - Current weather from WeatherAPI.com
- `get_weather_hourly_by_group_id()` - 24-hour forecast from WeatherAPI.com
- `get_weather_by_group_id()` - Current weather from Google Weather API (legacy)

## Development Workflows

### Environment Setup
```bash
# Windows - Create and activate venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment - copy env-example to .env and set:
# MONGO_URI, MONGODB_NAME, SECRET_KEY, collection names
```

### Running the Application
```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --port 8000

# Or use built-in dev runner
python -m app.main
```

### Testing
```bash
pytest  # Runs all tests in tests/

# Tests use ASGITransport pattern (see test_main.py):
transport = ASGITransport(app=app)
async with AsyncClient(transport=transport, base_url="http://test") as client:
    response = await client.get("/")
```

## Database Access

### Motor Async Collections
Database connections initialized in [database.py](../app/db/database.py):
```python
from app.db.database import notification_collection

# Async operations
doc = await notification_collection.find_one(query)
docs = await notification_collection.find(query).skip(skip).limit(limit).to_list()
total = await notification_collection.count_documents(query)
```

### Pagination Pattern
See [notification_repo.py](../app/repositories/notification_repo.py#L66-L78) for standard implementation:
- Calculate `skip = (page - 1) * page_size`
- Get total count first, then fetch records
- Return `AppBasePagingRes` with `is_full` flag

## Key Conventions

### Route Registration
All routes registered via `init_routes()` in [main.py](../app/main.py#L105-L110):
```python
BASE_URL = "/api/v1"
app.include_router(router, prefix=BASE_URL, tags=["API Name"])
```

### Configuration
Environment variables loaded via [config.py](../app/configs/config.py) using `python-dotenv`. Import as:
```python
from app.configs import config
config.MONGO_URI  # Access vars
config.GOOGLE_MAPS_API_KEY  # For Google Weather/Geocoding APIs
config.WEATHER_API_KEY  # For WeatherAPI.com
```

### Logging
Use configured logger from [logger.py](../app/logger/logger.py):
```python
from app.logger.logger import logger
logger.info("message")  # Auto-rotates daily, 7-day retention
```

### Enums
Use string-based Enums (see [notification_model.py](../app/models/notification_model.py#L9-L11)):
```python
class Status(str, Enum):
    ACTIVE = "active"
```

## Common Gotchas
- MongoDB requires Binary UUIDs, not strings - always convert
- Pydantic models use `populate_by_name=True` for `_id` aliasing
- Exception handlers are global - don't return raw HTTPExceptions from endpoints
- CORS is wide open (`allow_origins=["*"]`) - configure appropriately for production
- Notification filtering logic is complex - review [notification_repo.py](../app/repositories/notification_repo.py#L22-L45) when modifying

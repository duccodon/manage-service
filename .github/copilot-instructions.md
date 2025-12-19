# Copilot Instructions for manage-service

## Project Overview
FastAPI microservice for managing notifications in the cxview system. Uses MongoDB with Motor (async driver), JWT authentication, and a layered architecture (router → service → repository).

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

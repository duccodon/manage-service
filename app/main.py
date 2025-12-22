from datetime import datetime
import re
from app.configs import config
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.db import database
from app.routes import location_router, notification_router, weather_router
from app.logger.logger import logger
from app.schemas.base import AppBaseResponseError
import uvicorn


# Lifespan context replaces startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    yield
    logger.info("App shutdown")


# FastAPI app
app = FastAPI(
    title="My API",
    description="This is a sample API",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={"syntaxHighlight": False},
    lifespan=lifespan,
    redirect_slashes=False,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Book Management API"}


@app.get("/healthcheck/database")
async def get_welcome_message():
    try:
        ping = await database.database.command("ping")
        success = ping.get("ok", False)
        return {
            "timestamp": str(datetime.now()),
            "connected": bool(success),
            "status": "connected" if success else "not-connected",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed") from e


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(_: Request, exc: StarletteHTTPException):
    return AppBaseResponseError(
        message=exc.detail,
        status_code=exc.status_code,
    ).to_json(exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = exc.errors()
    message = ", ".join(
        map(lambda x: f"{re.sub(r'^Value error, ?', '', x.get('msg'))}", errors)
    )
    return AppBaseResponseError(message, status.HTTP_400_BAD_REQUEST).to_json(
        status.HTTP_400_BAD_REQUEST
    )


@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    return AppBaseResponseError(
        str(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
    ).to_json(status.HTTP_500_INTERNAL_SERVER_ERROR)


# Init all routes
BASE_URL = "/api/v1"


def init_routes(app: FastAPI):
    app.include_router(
        notification_router.router, prefix=BASE_URL, tags=["Notification API"]
    )
    app.include_router(
        location_router.router, prefix=BASE_URL, tags=["Location API"]
    )
    app.include_router(
        weather_router.router, prefix=BASE_URL, tags=["Weather API"]
    )


init_routes(app)

# Dev run
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=config.PORT, reload=True)

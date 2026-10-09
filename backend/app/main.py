"""FastAPI application entry point.

Responsibilities of this module:

* create and configure the application,
* register CORS for the deployed frontend origin(s),
* convert domain errors into the standard ``{success, data, message}``
  envelope with the correct HTTP status code,
* log every business event and every unhandled error,
* expose the liveness endpoints used by the hosting platform.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api import (
    ai,
    analytics,
    annotation_reviews,
    annotation_tasks,
    annotations,
    assignments,
    auth,
    datasets,
    exports,
    jobs,
    reviews,
    users,
)
from backend.app.core.config import settings, verify_runtime_settings
from backend.app.core.database import initialize_database
from backend.app.core.errors import MarketplaceError
from backend.app.core.logging import configure_logging, get_logger
from backend.app.core.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from backend.app.schemas.response import (
    APIResponse,
    error_response,
    success_response,
)

configure_logging()

logger = get_logger(__name__)

for _problem in verify_runtime_settings():
    logger.warning("Configuration warning: %s", _problem)

UNLOGGED_PATHS = {
    "/health",
    "/api/health",
    "/favicon.ico",
}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Bootstrap the database before serving requests."""
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for the AI Dataset Labeling Marketplace: datasets, "
        "labeling jobs, annotation tasks, annotations, quality review, "
        "progress tracking, dataset export and the AI annotation assistant."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)


# Registered before CORS on purpose: Starlette executes the middleware that was
# added last as the outermost layer, so CORS keeps wrapping every other layer
# and a throttled request still receives the CORS headers the browser expects.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log method, path, status code and duration of every request."""
    started = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started) * 1000

    if (
        request.url.path not in UNLOGGED_PATHS
        and not request.url.path.startswith("/docs")
        and not request.url.path.startswith("/openapi")
    ):
        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

    return response


def _envelope(
    message: str,
    status_code: int,
) -> JSONResponse:
    """Build a JSON error response using the shared envelope."""
    return JSONResponse(
        status_code=status_code,
        content=error_response(message).model_dump(),
    )


@app.exception_handler(MarketplaceError)
async def marketplace_error_handler(
    request: Request,
    error: MarketplaceError,
) -> JSONResponse:
    """Map domain errors to their HTTP status code."""
    logger.warning(
        "%s %s failed with %s: %s",
        request.method,
        request.url.path,
        type(error).__name__,
        error,
    )

    return _envelope(str(error), error.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Return a readable message for invalid request payloads."""
    details = [
        {
            "field": ".".join(str(part) for part in item.get("loc", ())),
            "message": item.get("msg", "Invalid value."),
        }
        for item in error.errors()
    ]

    logger.info(
        "%s %s rejected: %s validation error(s).",
        request.method,
        request.url.path,
        len(details),
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": details,
            "message": "The submitted data failed validation.",
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    error: StarletteHTTPException,
) -> JSONResponse:
    """Keep plain HTTP errors inside the shared envelope."""
    return _envelope(
        str(error.detail),
        error.status_code,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    """Log unexpected failures without leaking internals to clients."""
    logger.exception(
        "Unhandled error on %s %s.",
        request.method,
        request.url.path,
    )

    return _envelope(
        "An unexpected server error occurred. Please try again.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


for api_router in (
    auth.router,
    users.router,
    datasets.router,
    jobs.router,
    assignments.router,
    annotation_tasks.router,
    annotations.router,
    annotation_reviews.router,
    reviews.router,
    analytics.router,
    exports.router,
    ai.router,
):
    app.include_router(api_router)


@app.get(
    "/",
    response_model=APIResponse[dict],
    tags=["Health"],
    summary="API root",
)
def read_root() -> APIResponse[dict]:
    """Return basic service information."""
    return success_response(
        {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "status": "running",
            "docs": "/docs",
        },
        "AI Dataset Labeling Marketplace API is running.",
    )


@app.get(
    "/health",
    response_model=APIResponse[dict],
    tags=["Health"],
    summary="Liveness probe",
)
@app.get(
    "/api/health",
    response_model=APIResponse[dict],
    tags=["Health"],
    summary="Liveness probe (API prefix)",
    include_in_schema=False,
)
def health_check() -> APIResponse[dict]:
    """Return the service health status used by hosting smoke tests."""
    return success_response(
        {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        },
        "Service is healthy.",
    )

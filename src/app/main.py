# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.api.api_v1.router import api_router
from app.core.config import settings
from app.schemas.base import Status
from app.services.risk import risk_service

logger = logging.getLogger("uvicorn.error")

# Sentry
if isinstance(settings.SENTRY_DSN, str):
    sentry_sdk.init(
        settings.SENTRY_DSN,
        enable_tracing=False,
        traces_sample_rate=0.0,
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
        ],
        release=settings.VERSION,
        server_name=settings.SERVER_NAME,
        debug=settings.DEBUG,
        environment=None if settings.DEBUG else "production",
    )
    logger.info(f"Sentry middleware enabled on server {settings.SERVER_NAME}")


def _seconds_until_next_utc_hour(target_hour: int) -> float:
    now = datetime.now(tz=timezone.utc)
    target = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def _risk_refresh_loop() -> None:
    while True:
        try:
            await asyncio.sleep(_seconds_until_next_utc_hour(settings.RISK_REFRESH_HOUR_UTC))
            await risk_service.refresh()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Risk refresh loop iteration failed; continuing")


@asynccontextmanager
async def lifespan(_: FastAPI):
    if risk_service.is_configured:
        await risk_service.refresh()
        task = asyncio.create_task(_risk_refresh_loop())
    else:
        task = None
        logger.info("Risk API not configured; skipping daily refresh")
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    debug=settings.DEBUG,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,
    lifespan=lifespan,
)


# Healthcheck
@app.get("/status", status_code=status.HTTP_200_OK, summary="Healthcheck for the API", include_in_schema=False)
def get_status() -> Status:
    return Status(status="ok")


# Routing
app.include_router(api_router, prefix=settings.API_V1_STR)


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if isinstance(settings.SENTRY_DSN, str):
    # Sentry middleware is compatible at runtime
    app.add_middleware(SentryAsgiMiddleware)  # type: ignore[arg-type]


# Overrides swagger to include favicon
@app.get("/docs", include_in_schema=False)
def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=settings.PROJECT_NAME,
        swagger_favicon_url="https://pyronear.org/img/favicon.ico",
        # Remove schemas from swagger
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )


# OpenAPI config
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    # https://fastapi.tiangolo.com/tutorial/metadata/
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.PROJECT_DESCRIPTION,
        routes=app.routes,
        license_info={"name": "Apache 2.0", "url": "http://www.apache.org/licenses/LICENSE-2.0.html"},
        contact={
            "name": "API support",
            "email": settings.SUPPORT_EMAIL,
            "url": "https://github.com/pyronear/pyro-api/issues",
        },
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://pyronear.org/img/logo_letters.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]
if settings.PROMETHEUS_ENABLED:
    Instrumentator(
        excluded_handlers=["/metrics", "/docs", ".*openapi.json"],
    ).instrument(app).expose(app, include_in_schema=False)
    logger.info("Collecting performance data with Prometheus")

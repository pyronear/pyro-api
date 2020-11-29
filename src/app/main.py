import time
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from app import config as cfg
from app.api.routes import login, users, sites, events, devices, media, installations, alerts, accesses
from app.db import engine, metadata, database, init_db

metadata.create_all(engine)

# Sentry
if isinstance(cfg.SENTRY_DSN, str):
    sentry_sdk.init(
        cfg.SENTRY_DSN,
        traces_sample_rate=1.0
    )

app = FastAPI(title=cfg.PROJECT_NAME, description=cfg.PROJECT_DESCRIPTION, debug=cfg.DEBUG, version=cfg.VERSION)


# Database connection
@app.on_event("startup")
async def startup():
    await database.connect()
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Routing
app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(sites.router, prefix="/sites", tags=["sites"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(installations.router, prefix="/installations", tags=["installations"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(accesses.router, prefix="/accesses", tags=["accesses"])


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if isinstance(cfg.SENTRY_DSN, str):
    @app.middleware("http")
    async def sentry_exception(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("request", request)
                scope.user = {
                    "ip_address": request.client.host,
                }
                sentry_sdk.capture_exception(e)
            raise e


# Docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=cfg.PROJECT_NAME,
        version=cfg.VERSION,
        description=cfg.PROJECT_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": cfg.LOGO_URL}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

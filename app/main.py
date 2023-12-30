# app/main.py

from app.config import settings
from app.models.user import UserAccount
from app.routes import (
    auth_router,
    business_router,
    user_group_router,
    user_router,
    wallet_router,
    ipg_router,
    wallet_transactions_router,
)
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware

from owjcommon.exceptions import (
    OWJException,
    http_exception_handler,
    owj_exception_handler,
    request_validation_exception_handler,
)


def custom_generate_unique_id(route):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="OWJ CRS Account Microservice",
    description="This is the API documentation for the OWJ CRS Account Service.",
    version="1.0.0",
    generate_unique_id_function=custom_generate_unique_id,
    servers=[
        {"url": "https://account.owj.app", "description": "Production environment"},
        {"url": "http://localhost:8000", "description": "Local environment"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_PREFIX = "/api/account/v1"

app.include_router(user_router, prefix=BASE_PREFIX + "/user")
app.include_router(user_group_router, prefix=BASE_PREFIX + "/group")
app.include_router(business_router, prefix=BASE_PREFIX + "/business")
app.include_router(auth_router, prefix=BASE_PREFIX + "/auth")
app.include_router(
    wallet_transactions_router, prefix=BASE_PREFIX + "/wallet/transaction"
)
app.include_router(wallet_router, prefix=BASE_PREFIX + "/wallet")
app.include_router(ipg_router, prefix=BASE_PREFIX + "/ipg")


register_tortoise(
    app,
    config={
        "connections": {"default": settings.tortoise_orm.db_connection},
        "apps": {
            "models": {
                "models": ["app.models"],
                "default_connection": "default",
            }
        },
    },
    # This will create the DB tables on startup (useful for development)
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.exception_handler(OWJException)
async def _owj_exception_handler(request, exc):
    return await owj_exception_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request, exc):
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def _request_validation_exception_handler(request, exc):
    return await request_validation_exception_handler(request, exc)


# on start up create account
@app.on_event("startup")
async def startup_event():
    return

from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasicCredentials
from starlette.config import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth.fastapi_auth import verify_credentials, get_secret_key
from db.mdb_client import client_motors
from routers import hotels, hotels_travel_us
from db.redis_client import AsyncRedisClient
from dotenv import load_dotenv


# Custom FastAPI app to hold state
class CustomFastAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = None


# Initialize FastAPI app
app = CustomFastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load environment variables
config = Config(".env")
load_dotenv()

# CORS settings
origins = ["*", "http://localhost", "http://localhost:3000", "http://192.168.110.128"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


# Dependency to get the Redis client
def get_redis_client(request: CustomFastAPI):
    return request.redis_client


# Include routers
prefix_path = '/api/v1'
app.include_router(hotels.router, prefix=f'{prefix_path}/hotels', dependencies=[Depends(get_secret_key)],
                   tags=["Hotels"])
app.include_router(hotels_travel_us.router, prefix=f'{prefix_path}/tus', dependencies=[Depends(get_secret_key)],
                   tags=["Travel US"])


# Startup event to initialize Redis
@app.on_event("startup")
async def startup():
    # logger.info("Starting up the server & connecting to redis & mongodb servers")
    app.redis_client = await AsyncRedisClient.get_instance()
    app.mdb_client = client_motors


# Shutdown event to close Redis connection
@app.on_event("shutdown")
async def shutdown():
    await app.redis_client.close()


# Custom OpenAPI and Docs Endpoints
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="Booking.com API",
        version="v25.07.2024",
        description="Booking.com Unofficial API",
        routes=app.routes,
    )
    return openapi_schema


@app.get("/ping", include_in_schema=True)  # or simply remove `include_in_schema`
async def ping():
    return {"status": "alive"}


@app.get("/docs", include_in_schema=False)
async def custom_docs_url(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title,
                               swagger_css_url="/static/swagger_ui_dark.min.css")


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_url(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(openapi_url="/openapi.json", title=app.title)

# from dotenv import load_dotenv
# from fastapi import FastAPI, Depends
# from fastapi.security import HTTPBasicCredentials
# from starlette.config import Config
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from auth.fastapi_auth import verify_credentials, get_secret_key
# from routers import hotels, hotels_travel_us
# from db.clientRedis import AsyncRedisClient
# from contextlib import asynccontextmanager
#
#
# # Custom FastAPI app to hold state
# class CustomFastAPI(FastAPI):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.redis_client = None
#
#
# # Initialize FastAPI app
# app = CustomFastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# app.mount("/static", StaticFiles(directory="static"), name="static")
#
# # Load environment variables
# config = Config(".env")
# load_dotenv()
#
# # CORS settings
# origins = ["*", "http://localhost", "http://localhost:3000", "http://192.168.110.128"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
#     allow_headers=["*"],
#     expose_headers=["Content-Disposition"]
# )
#
#
# # Dependency to get the Redis client
# def get_redis_client(request: CustomFastAPI):
#     return request.redis_client
#
#
# # # Include routers
# # app.include_router(hotels.router)
# prefix_path = '/api/v1'
# app.include_router(hotels.router, prefix=f'{prefix_path}/hotels', dependencies=[Depends(get_secret_key)],
#                    tags=["Hotels"])
# app.include_router(hotels_travel_us.router, prefix=f'{prefix_path}/tus', dependencies=[Depends(get_secret_key)],
#                    tags=["Travel US"])
#
#
# # Lifespan context manager for application startup and shutdown
# @asynccontextmanager
# async def lifespan(app: CustomFastAPI):
#     app.redis_client = await AsyncRedisClient.get_instance()
#     yield
#     await app.redis_client.close()
#
#
# app.lifespan_context = lifespan
#
#
# # Custom OpenAPI and Docs Endpoints
# @app.get("/openapi.json", include_in_schema=False)
# async def get_open_api_endpoint():
#     from fastapi.openapi.utils import get_openapi
#     openapi_schema = get_openapi(
#         title="Booking.com API",
#         version="v25.07.2024",
#         description="Booking.com Unofficial API",
#         routes=app.routes,
#     )
#     return openapi_schema
#
#
# @app.get("/ping", include_in_schema=False)
# async def ping():
#     return {"status": "alive"}
#
#
# @app.get("/docs", include_in_schema=False)
# async def custom_docs_url(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
#     from fastapi.openapi.docs import get_swagger_ui_html
#     return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title,
#                                swagger_css_url="/static/swagger_ui_dark.min.css")
#
#
# @app.get("/redoc", include_in_schema=False)
# async def custom_redoc_url(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
#     from fastapi.openapi.docs import get_redoc_html
#     return get_redoc_html(openapi_url="/openapi.json", title=app.title)

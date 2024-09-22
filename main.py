from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasicCredentials
from starlette.config import Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth.fastapi_auth import verify_credentials, get_secret_key
from db.mdb_client import client_motors
from db.redis_client import AsyncRedisClient
from dotenv import load_dotenv

from routers import hotels


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
app.include_router(hotels.router, prefix=f'{prefix_path}/data', dependencies=[Depends(get_secret_key)],
                   tags=["Hotels"])


@app.on_event("startup")
async def startup():
    # Connect to Redis
    app.redis_client = await AsyncRedisClient.get_instance()
    app.mdb_client = client_motors.booking  # MongoDB client instance

    # Clear all Redis cache
    try:
        await app.redis_client.flushdb()
        print("Successfully cleared all Redis cache.")
    except Exception as e:
        print(f"Error clearing Redis cache: {str(e)}")

    # # Optionally: Perform other startup tasks (e.g., connecting to MongoDB)
    # print("Connected to MongoDB and Redis.")


# Shutdown event to close Redis connection
@app.on_event("shutdown")
async def shutdown():
    await app.redis_client.close()


# Custom OpenAPI and Docs Endpoints
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="The Travel Office US API",
        version="v25.07.2024",
        description="API for hotels, user reviews, and travel data with Redis caching and MongoDB storage.",
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
import os
import secrets
from fastapi import HTTPException, Depends, security, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from datetime import datetime, timedelta
from dotenv import load_dotenv
from db.redis_client import AsyncRedisClient

load_dotenv()

SECRET_KEY = os.environ["BEARER_SECRET_KEY"]

# Create instances of HTTPBearer and HTTPBasic
http_bearer = security.HTTPBearer()
security_basic = HTTPBasic()


async def get_secret_key(security_payload: security.HTTPAuthorizationCredentials = Depends(http_bearer)):
    authorization = security_payload.credentials
    if not authorization or SECRET_KEY not in authorization:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return authorization


async def get_login_attempts(username: str):
    redis_client = await AsyncRedisClient.get_instance()
    attempts = await redis_client.get(f"{username}:attempts")
    if attempts:
        return int(attempts)
    return 0


async def get_last_attempt_time(username: str):
    redis_client = await AsyncRedisClient.get_instance()
    last_time = await redis_client.get(f"{username}:last_attempt")
    if last_time:
        return datetime.fromtimestamp(float(last_time))
    return None


async def set_failed_login(username: str, attempts: int, last_attempt_time: datetime):
    redis_client = await AsyncRedisClient.get_instance()
    await redis_client.set(f"{username}:attempts", attempts, ex=300)  # 5 minutes expiration
    await redis_client.set(f"{username}:last_attempt", last_attempt_time.timestamp(), ex=300)
    print(f"Failed login attempt for username: {username}. Attempts: {attempts}")


async def reset_login_attempts(username: str):
    redis_client = await AsyncRedisClient.get_instance()
    await redis_client.delete(f"{username}:attempts", f"{username}:last_attempt")


async def verify_credentials(credentials: HTTPBasicCredentials = Depends(security_basic)):
    username = credentials.username
    current_time = datetime.now()

    # Check if the username is currently blocked
    attempts = await get_login_attempts(username)
    last_attempt_time = await get_last_attempt_time(username)

    if attempts >= 5 and last_attempt_time and (current_time - last_attempt_time) < timedelta(minutes=5):
        print(f"Too many login attempts for username: {username}.")
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Too many login attempts. Please try again later.")

    correct_username = secrets.compare_digest(credentials.username, os.environ["FASTAPI_UI_USERNAME"])
    correct_password = secrets.compare_digest(credentials.password, os.environ["FASTAPI_UI_PASSWORD"])

    if not (correct_username and correct_password):
        await set_failed_login(username, attempts + 1, current_time)
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Reset the count on successful login
    await reset_login_attempts(username)
    print(f"Successful login for username: {username}.")
    return credentials

from fastapi import HTTPException, Response, Request
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import jwt
from models.auth_models import LoginRequest

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")

def authenticate_user(login_request: LoginRequest, response: Response):
    if login_request.username == USERNAME and login_request.password == PASSWORD:
        expiration = datetime.now(timezone.utc) + timedelta(hours=48)
        token = jwt.encode({"exp": expiration.timestamp()}, SECRET_KEY, algorithm="HS256")
        response.set_cookie(key="token", value=token, httponly=True, secure=True, samesite="none", domain="investment-helper.com")
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

def auth_status(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expiration = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        if expiration < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")
        return {"status": "authenticated"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def logout(response: Response):
    response.delete_cookie(key="token")
    return {"status": "success", "message": "Logged out successfully"}

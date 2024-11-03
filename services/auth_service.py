from fastapi import HTTPException, Request
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import jwt
from models.auth_models import LoginRequest

# 환경 변수 로드
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")


# 1. 사용자 인증 함수 - JWT 토큰 응답 본문에 포함
def authenticate_user(login_request: LoginRequest):
    if login_request.username == USERNAME and login_request.password == PASSWORD:
        # 토큰 생성 및 만료 시간 설정
        expiration = datetime.now(timezone.utc) + timedelta(hours=48)
        token = jwt.encode({"exp": expiration.timestamp()}, SECRET_KEY, algorithm="HS256")

        # 응답 본문에 JWT 토큰 포함
        return {"status": "success", "message": "Login successful", "token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


# 2. 인증 상태 확인 함수 - Authorization 헤더에서 JWT 토큰 확인
def auth_status(request: Request):
    # 헤더에서 토큰 가져오기
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]  # "Bearer <token>" 형식에서 토큰만 추출

    try:
        # JWT 토큰 디코드 및 만료 확인
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expiration = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)

        if expiration < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token expired")

        return {"status": "authenticated"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

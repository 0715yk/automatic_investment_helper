from fastapi import HTTPException, Response, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import jwt

# .env 파일 로드
load_dotenv()

# 환경 변수에서 로그인 정보 가져오기
USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class LoginRequest(BaseModel):
    username: str
    password: str


def authenticate_user(login_request: LoginRequest, response: Response):
    # 아이디와 비밀번호 확인
    if login_request.username == USERNAME and login_request.password == PASSWORD:
        # JWT 토큰 생성
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({"exp": expiration}, SECRET_KEY, algorithm="HS256")

        # 토큰을 쿠키에 설정
        response.set_cookie(key="token", value=token, httponly=True)
        return {"status": "success", "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

def auth_status(request: Request):
    token = request.cookies.get("token")  # 쿠키에서 토큰 가져오기
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # JWT 토큰 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expiration = datetime.fromtimestamp(payload.get("exp"))
        if expiration < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")

        return {"status": "authenticated"}  # 인증 성공 시 응답
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def logout(response: Response):
    # 쿠키에서 토큰 삭제
    response.delete_cookie(key="token")
    return {"status": "success", "message": "Logged out successfully"}

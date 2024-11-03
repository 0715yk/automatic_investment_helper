from fastapi import APIRouter, Request, Response
from models.auth_models import LoginRequest
from services.auth_service import authenticate_user, auth_status

router = APIRouter()

@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    # 로그인 요청 처리 및 JWT 토큰 생성 후 응답
    return authenticate_user(login_request, response)

@router.get("/auth/status")
async def check_auth_status(request: Request):
    # Authorization 헤더에서 JWT 토큰을 가져와 인증 상태 확인
    return auth_status(request)

from fastapi import APIRouter, Request, Response
from models.auth_models import LoginRequest
from services.auth_service import authenticate_user, auth_status, logout

router = APIRouter()

@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    return authenticate_user(login_request, response)

@router.get("/auth/status")
async def check_auth_status(request: Request):
    return auth_status(request)

@router.post("/logout")
async def logout_user(response: Response):
    return logout(response)

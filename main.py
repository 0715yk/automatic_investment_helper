from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from upbit import get_account_info
from account import LoginRequest, authenticate_user, auth_status, logout

# FastAPI 인스턴스 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # 쿠키를 포함하여 요청을 허용
    allow_origins=["http://localhost:3000","https://investment-helper-fe-hnxi.vercel.app"],  # 필요한 경우 클라이언트 주소를 추가
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인증 상태 확인 엔드포인트
@app.get("/api/auth/status")
async def check_auth_status(request: Request):
    return auth_status(request)

# 로그인
@app.post("/api/login")
async def login(login_request: LoginRequest, response: Response):
    return authenticate_user(login_request, response)

# 로그아웃 엔드포인트
@app.post("/api/logout")
async def logout_user(response: Response):
    return logout(response)

# 특정 코인 잔고 가져오기
@app.get("/api/account-info")
async def account_info():
    try:
        account_info = get_account_info()
        return {"status": "success", "data": account_info}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
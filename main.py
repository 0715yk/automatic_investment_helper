from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth  # 분리한 라우터 모듈들 가져오기
from routers import account
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000", "https://investment-helper-fe-hnxi.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api")
app.include_router(account.router, prefix="/api")
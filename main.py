from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, account
# from routers.shiba_router import router as shiba_router
from routers.portfolio_router import router as portfolio_router
from routers import bollinger

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
# app.include_router(shiba_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(bollinger.router,  prefix="/api")
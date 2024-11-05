# routers/portfolio_router.py
from fastapi import APIRouter, WebSocket
from services.portfolio_service import fetch_portfolio
from dotenv import load_dotenv
import os

router = APIRouter()
load_dotenv()

# 환경변수나 설정에서 가져오기
UPBIT_ACCESS_KEY = os.getenv("UPBIT_OPEN_API_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_OPEN_API_SECRET_KEY")

@router.websocket("/ws/portfolio")
async def portfolio_websocket(websocket: WebSocket):
    await websocket.accept()
    await fetch_portfolio(websocket, UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
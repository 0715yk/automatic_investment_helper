# routers/shiba_router.py

from fastapi import APIRouter, WebSocket
from services.shiba_service import fetch_shiba_price

router = APIRouter()

@router.websocket("/ws/shiba-price")
async def shiba_price_websocket(websocket: WebSocket):
    await websocket.accept()
    await fetch_shiba_price(websocket)

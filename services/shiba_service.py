# services/shiba_service.py

import pyupbit
import datetime
import asyncio
from fastapi import WebSocketDisconnect

async def fetch_shiba_price(websocket):
    try:
        while True:
            price = pyupbit.get_current_price("KRW-SHIB")
            if price:
                message = {
                    "price": price,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                await websocket.send_json(message)
                await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass  # 정상적인 연결 종료는 무시
    except Exception as e:
        print(f"Unexpected error: {e}")  # 실제 에러만 출력
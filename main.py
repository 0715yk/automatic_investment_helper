from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pyupbit
import ssl
import threading
import json
import websocket
import asyncio
from queue import Queue
import time
import pandas as pd
import datetime
import requests
from upbit import get_account_info  # upbit.py에서 get_balance 함수 가져오기

# lifespan을 사용한 서버 시작 시 초기화 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    # await get_top_coins()  # 상위 5개 코인 초기화
    # start_price_websocket()  # 각 코인에 대해 WebSocket 스레드 시작
    # update_thread = threading.Thread(target=update_bollinger_bands_periodically, daemon=True)
    # update_thread.start()  # 볼린저 밴드 업데이트 스레드 시작
    yield  # 애플리케이션 실행
    # 종료 시 필요한 정리 작업 (없으면 비워둠)

# FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://investment-helper-fe-hnxi-tr6l9elec-0715yks-projects.vercel.app/"],  # 필요한 경우 클라이언트 주소를 추가
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSL 문제 해결 (SSL 인증서 무시)
# try:
#     _create_default_https_context = ssl._create_default_https_context
#     ssl._create_default_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass

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

# 체결 강도 상위 코인 목록을 저장
top_coins = []
price_queue = Queue()

# 코인별 볼린저 밴드 및 매매 신호 데이터 저장
coin_data = {}

# 일일 체결 강도 순위 상위 5개 코인을 가져오는 API 엔드포인트
@app.get("/top-coins/")
async def get_top_coins():
    # 전체 마켓 목록을 가져오는 엔드포인트
    print('hello')
    market_url = "https://api.upbit.com/v1/market/all"
    market_response = requests.get(market_url)

    if market_response.status_code == 200:
        markets = market_response.json()

        krw_markets = [market['market'] for market in markets if market['market'].startswith("KRW-")]

        # KRW 마켓만 가져와 일일 체결 강도 순위 기준으로 정렬
        ticker_url = f"https://api.upbit.com/v1/ticker?markets={','.join(krw_markets)}"
        ticker_response = requests.get(ticker_url)

        if ticker_response.status_code == 200:
            ticker_data = ticker_response.json()

            # acc_trade_price_24h가 None이 아닌 항목만 필터링하고 정렬
            valid_data = [coin for coin in ticker_data if coin.get("acc_trade_price_24h") is not None]
            sorted_data = sorted(valid_data, key=lambda x: x["acc_trade_price_24h"], reverse=True)
            top_coins_data = sorted_data[:5]

            global top_coins
            top_coins = [coin["market"] for coin in top_coins_data]

            # 코인 데이터를 초기화
            global coin_data
            coin_data = {
                symbol: {"price": None, "upper": None, "lower": None, "middle": None, "signal": None, "timestamp": None}
                for symbol in top_coins}
            return {"top_coins": top_coins}

    return {"error": "Failed to fetch data"}

# 볼린저 밴드 계산 함수
def calculate_bollinger_bands(ticker, interval="day", count=100):
    df = pyupbit.get_ohlcv(ticker=ticker, interval=interval, count=count)

    # Calculate moving average and standard deviation
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['STD20'] = df['close'].rolling(window=20).std()

    # Fill NaN values with 0.0 to ensure calculations can proceed
    df['MA20'] = df['MA20'].fillna(0.0)
    df['STD20'] = df['STD20'].fillna(0.0)

    # Calculate upper and lower Bollinger Bands
    upper_band = df['MA20'] + (2 * df['STD20'])
    lower_band = df['MA20'] - (2 * df['STD20'])
    middle_band = df['MA20']

    # Ensure there is at least one valid row after filling NaN values
    if not df.empty:
        # Save the latest Bollinger Band values, ensuring no None or NaN values
        coin_data[ticker]["upper"] = float(upper_band.iloc[-1]) if upper_band.iloc[-1] is not None else 0.0
        coin_data[ticker]["lower"] = float(lower_band.iloc[-1]) if lower_band.iloc[-1] is not None else 0.0
        coin_data[ticker]["middle"] = float(middle_band.iloc[-1]) if middle_band.iloc[-1] is not None else 0.0
    else:
        # Handle cases where there isn't enough data
        print(f"Not enough data to calculate Bollinger Bands for {ticker}")
        coin_data[ticker]["upper"] = 0.0
        coin_data[ticker]["lower"] = 0.0
        coin_data[ticker]["middle"] = 0.0

# 매매 전략 적용 함수
def apply_bollinger_band_strategy(ticker, trade_price):
    upper_band = coin_data[ticker]["upper"]
    lower_band = coin_data[ticker]["lower"]
    middle_band = coin_data[ticker]["middle"]
    current_time = datetime.datetime.now()

    # 매수/매도/관망 신호 설정
    if trade_price < lower_band:
        signal = "BUY"
    elif trade_price > upper_band:
        signal = "SELL"
    else:
        signal = "HOLD"

    # 신호 업데이트 및 큐에 추가
    coin_data[ticker].update({
        "price": trade_price,
        "signal": signal,
        "timestamp": current_time
    })
    price_queue.put({"symbol": ticker, "price": trade_price, "signal": signal, "timestamp": current_time})

# 모든 코인의 볼린저 밴드를 일정 간격으로 업데이트
def update_bollinger_bands_periodically():
    while True:
        for ticker in top_coins:
            calculate_bollinger_bands(ticker)  # 볼린저 밴드 갱신
        time.sleep(60)  # 1분마다 업데이트

# WebSocket을 통해 실시간 가격 및 신호 전송
@app.websocket("/real-time-prices")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not price_queue.empty():
                data = price_queue.get()
                await websocket.send_json(data)  # 클라이언트에 데이터 전송
            await asyncio.sleep(1)  # 1초 간격으로 전송
    except WebSocketDisconnect:
        print("Client disconnected")

# 실시간 가격을 가져오고 매매 전략을 적용하는 WebSocket 함수 (각 코인별 WebSocket 연결)
def start_price_websocket(ticker):
    def on_message(ws, message):
        data = json.loads(message)
        trade_price = data.get("tp")

        # 매매 전략 적용
        if trade_price:
            apply_bollinger_band_strategy(ticker, trade_price)

    def on_error(ws, error):
        print("Error:", error)

    def on_close(ws, close_status_code, close_msg):
        print(f"WebSocket closed for {ticker}: {close_status_code} - {close_msg}")

    def on_open(ws):
        subscribe_message = [{"ticket": "test"}, {"type": "ticker", "codes": [ticker]}, {"format": "SIMPLE"}]
        ws.send(json.dumps(subscribe_message))

    # WebSocketApp 인스턴스를 생성하고 설정을 완료
    ws = websocket.WebSocketApp(
        "wss://api.upbit.com/websocket/v1",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # SS
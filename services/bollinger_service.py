# services/bollinger_service.py

import pandas as pd
import numpy as np
import requests
from typing import Dict, Optional, List
import matplotlib.pyplot as plt
import io
import base64

def fetch_close_prices(coin_name: str, count: int = 100) -> Optional[np.ndarray]:
    """
    특정 코인의 최근 종가 데이터를 가져오는 함수.
    """
    url = f"https://api.upbit.com/v1/candles/days?market={coin_name}&count={count}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        close_prices = [float(day["trade_price"]) for day in data]
        close_prices.reverse()  # 최신 데이터가 뒤로 오도록 정렬
        return np.array(close_prices)
    except requests.exceptions.RequestException as e:
        print("Failed to fetch close prices:", e)
        return None


def calculate_bollinger_bands_series(close_prices: np.ndarray, window: int = 20, num_std_dev: int = 2):
    """그래프 그리기를 위한 전체 데이터 반환"""
    prices = pd.Series(close_prices)
    middle_band = prices.rolling(window=window).mean()
    std_dev = prices.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)
    return upper_band, middle_band, lower_band

# 그래프 그리는 함수
def plot_bollinger_bands(coin_name: str, close_prices: np.ndarray) -> str:
    """
    볼린저 밴드 그래프를 생성하고 base64 인코딩된 이미지를 반환하는 함수
    """
    upper_band, middle_band, lower_band = calculate_bollinger_bands_series(close_prices)

    plt.figure(figsize=(12, 6))
    plt.plot(close_prices, label='Close Price', color='black')
    plt.plot(upper_band, label='Upper Band', color='red', alpha=0.7)
    plt.plot(middle_band, label='Middle Band', color='blue', alpha=0.7)
    plt.plot(lower_band, label='Lower Band', color='red', alpha=0.7)

    plt.fill_between(range(len(close_prices)),
                     upper_band,
                     lower_band,
                     alpha=0.1,
                     color='gray')

    plt.title(f'{coin_name} Bollinger Bands')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)

    # 이미지를 메모리에 저장
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # base64로 인코딩
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return image_base64

# 사용 예시
def calculate_bollinger_bands(close_prices: np.ndarray, window: int = 20, num_std_dev: int = 2):
    """
    주어진 종가 데이터로 볼린저 밴드를 계산하는 함수.
    """
    prices = pd.Series(close_prices)
    middle_band = prices.rolling(window=window).mean()
    upper_band = middle_band + (prices.rolling(window=window).std() * num_std_dev)
    lower_band = middle_band - (prices.rolling(window=window).std() * num_std_dev)
    return upper_band.iloc[-1], middle_band.iloc[-1], lower_band.iloc[-1]


def is_bollinger_squeeze(close_prices: np.ndarray, threshold: float = 0.13) -> bool:
    """
    볼린저 스퀴즈 구간 여부를 확인하는 함수.
    """
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices)
    return bool((upper_band - lower_band) / middle_band < threshold)


def check_bollinger_squeeze_service(coin_name: str) -> Dict:
    """
    특정 코인의 볼린저 스퀴즈 여부를 확인하는 함수.
    """
    close_prices = fetch_close_prices(coin_name)
    if close_prices is None:
        return {"coin": coin_name, "is_squeeze": None, "error": "Failed to fetch data"}

    is_squeeze = is_bollinger_squeeze(close_prices)
    return {"coin": coin_name, "is_squeeze": is_squeeze}


def get_all_market_codes() -> Optional[List[Dict]]:
    """
    업비트의 모든 마켓 코드를 가져오는 함수
    """
    try:
        response = requests.get("https://api.upbit.com/v1/market/all")
        response.raise_for_status()

        # KRW 마켓만 필터링
        market_codes = [
            {
                "market": market["market"],
                "korean_name": market["korean_name"],
                "english_name": market["english_name"]
            }
            for market in response.json()
            if market["market"].startswith("KRW-")
        ]

        return market_codes
    except Exception as e:
        print("Failed to fetch market codes:", e)
        return None

def check_bollinger_breakout(coin_name: str, close_prices: np.ndarray) -> str:
    """
    볼린저 밴드 브레이크아웃 신호를 확인하는 함수
    """
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices)
    latest_close = close_prices[-1]

    # 신호 분석
    if latest_close > upper_band:
        return f"SELL"
    elif latest_close < lower_band:
        return f"BUY"
    else:
        return f"STAY"
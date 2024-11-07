from fastapi import APIRouter, Query, HTTPException
from services.bollinger_service import plot_bollinger_bands, check_bollinger_breakout, get_all_market_codes, check_bollinger_squeeze_service, fetch_close_prices

router = APIRouter()

@router.get("/get_all_market_codes")
async def get_market_codes():
    """
    모든 코인 목록을 가져오는 엔드포인트.
    Returns:
    - dict: 모든 시장 코드 리스트
    """
    codes = get_all_market_codes()
    if codes is None:
        return {"error": "Failed to fetch market codes"}
    return {"market_codes": codes}

@router.get("/check_bollinger_squeeze")
async def check_bollinger_squeeze(coin_name: str = Query(...)):
    """
    특정 코인의 볼린저 스퀴즈 여부를 확인하는 엔드포인트.
    Parameters:
    - coin_name (str): 코인 이름 (예: KRW-BTC)
    Returns:
    - dict: 스퀴즈 상태 및 오류 메시지
    """
    result = check_bollinger_squeeze_service(coin_name)
    return result


@router.get("/check_bollinger_breakout")
async def check_breakout(coin_name: str = Query(...)):
    """
    볼린저 밴드 브레이크아웃 체크 API 엔드포인트
    """
    close_prices = fetch_close_prices(coin_name)
    if close_prices is None:
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

    signal = check_bollinger_breakout(coin_name, close_prices)
    return {"coin": coin_name, "signal": signal}


@router.get("/bollinger_chart")
async def get_bollinger_chart(coin_name: str = Query(...)):
    """
    볼린저 밴드 차트를 반환하는 엔드포인트
    """
    close_prices = fetch_close_prices(coin_name)
    if close_prices is None:
        raise HTTPException(status_code=500, detail="Failed to fetch market data")
    try:
        chart_base64 = plot_bollinger_bands(coin_name, close_prices)
        return {
            "coin": coin_name,
            "chart": chart_base64,
            "chart_type": "base64"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate chart: {str(e)}")
# services/portfolio_service.py
import pyupbit
import asyncio
import logging
from typing import Dict, List
from models.portfolio import AssetBalance, Portfolio

logger = logging.getLogger(__name__)


class UpbitPortfolioService:
    def __init__(self, access_key: str, secret_key: str):
        self.upbit = pyupbit.Upbit(access_key, secret_key)

    async def get_portfolio_data(self) -> Portfolio:
        try:
            # 보유 자산 조회
            balances = self.upbit.get_balances()

            # 현재가 조회를 위한 티커 목록 생성
            tickers = [f"KRW-{balance['currency']}" for balance in balances if balance['currency'] != 'KRW']
            current_prices = {}

            # 현재가 조회
            for ticker in tickers:
                current_prices[ticker.split('-')[1]] = pyupbit.get_current_price(ticker)

            # 포트폴리오 데이터 구성
            asset_balances: List[AssetBalance] = []
            total_asset = 0
            total_profit_loss = 0

            # KRW 잔고 처리
            krw_balance = next((float(b['balance']) for b in balances if b['currency'] == 'KRW'), 0)
            total_asset += krw_balance

            # 암호화폐 잔고 처리
            for balance in balances:
                if balance['currency'] == 'KRW':
                    continue

                currency = balance['currency']
                amount = float(balance['balance'])
                avg_price = float(balance['avg_buy_price'])
                current_price = current_prices.get(currency)

                if current_price:
                    total_value = amount * current_price
                    invested_value = amount * avg_price
                    profit_loss = total_value - invested_value
                    profit_loss_rate = (profit_loss / invested_value * 100) if invested_value > 0 else 0

                    total_asset += total_value
                    total_profit_loss += profit_loss

                    asset_balances.append(AssetBalance(
                        currency=currency,
                        balance=amount,
                        avg_buy_price=avg_price,
                        current_price=current_price,
                        profit_loss=profit_loss,
                        profit_loss_rate=profit_loss_rate
                    ))

            total_invested = total_asset - total_profit_loss
            total_profit_loss_rate = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0

            return Portfolio(
                total_asset=total_asset,
                total_profit_loss=total_profit_loss,
                total_profit_loss_rate=total_profit_loss_rate,
                balances=asset_balances
            )

        except Exception as e:
            logger.error(f"Error fetching portfolio data: {e}")
            raise


async def fetch_portfolio(websocket, access_key: str, secret_key: str):
    service = UpbitPortfolioService(access_key, secret_key)

    try:
        while True:
            portfolio = await service.get_portfolio_data()
            await websocket.send_json(portfolio.dict())
            await asyncio.sleep(1)  # 1초 간격으로 업데이트
    except Exception as e:
        logger.error(f"Error in portfolio fetch: {e}")
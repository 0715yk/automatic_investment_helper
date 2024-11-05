# models/portfolio.py
from pydantic import BaseModel
from typing import List, Optional

class AssetBalance(BaseModel):
    currency: str
    balance: float
    avg_buy_price: float
    current_price: Optional[float]
    profit_loss: Optional[float]
    profit_loss_rate: Optional[float]

class Portfolio(BaseModel):
    total_asset: float
    total_profit_loss: float
    total_profit_loss_rate: float
    balances: List[AssetBalance]
# models/shiba_price.py

from pydantic import BaseModel

class ShibaPrice(BaseModel):
    price: float
    timestamp: str

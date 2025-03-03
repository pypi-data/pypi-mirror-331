from enum import Enum
from typing import Dict, Any
import logging

class PriceCondition(Enum):
    GROW_BY_PCT = "grow_by_pct"
    DEC_BY_PCT = "dec_by_pct"
    GROW_BY_AMT = "grow_by_amt"
    DEC_BY_AMT = "dec_by_amt"
        
def valid_price_condition_name(condition_name) -> bool:
    return condition_name in [condition.value for condition in PriceCondition]

def check_price_condition(condition_name: str, target_value: float, ticker_info: Dict[str, Any]) -> bool:
    logging.debug(f"Checking price condition {condition_name} with target value {target_value}")
    currentPrice: float = ticker_info.get('currentPrice', 0)
    prevClose: float = ticker_info.get('previousClose', 0)
    logging.debug(f"Current price: {currentPrice}, Previous close: {prevClose}")

    if condition_name == PriceCondition.GROW_BY_PCT.value:
        return (currentPrice - prevClose) / prevClose * 100 >= target_value
    elif condition_name == PriceCondition.DEC_BY_PCT.value:
        return (prevClose - currentPrice) / prevClose * 100 >= target_value
    elif condition_name == PriceCondition.GROW_BY_AMT.value:
        return (currentPrice - prevClose) >= target_value
    elif condition_name == PriceCondition.DEC_BY_AMT.value:
        return (prevClose - currentPrice) >= target_value
    else:
        return False
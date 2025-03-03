from enum import Enum
from typing import Dict, Any
import logging

class IndicatorCondition(Enum):
    BB_BELOW_LOWER = "bb_below_lower"
    BB_ABOVE_UPPER = "bb_above_upper"

def valid_indicator_condition_name(condition_name) -> bool:
    return condition_name in [condition.value for condition in IndicatorCondition]

def check_indicator_condition(condition_name: str, target_value: float, ticker_info: Dict[str, Any]) -> bool:
    logging.debug(f"Checking indicator condition {condition_name} with target value {target_value}")
    currentPrice: float = ticker_info.get('currentPrice', 0)
    bbLower: float = ticker_info.get('volatility_analysis', {}).get('BB_Lower', 0)
    bbUpper: float = ticker_info.get('volatility_analysis', {}).get('BB_Upper', 0)
    logging.debug(f"Current price: {currentPrice}, BB Lower: {bbLower}, BB Upper: {bbUpper}")
    
    if condition_name == IndicatorCondition.BB_BELOW_LOWER.value:
        return currentPrice < bbLower
    elif condition_name == IndicatorCondition.BB_ABOVE_UPPER.value:
        return currentPrice > bbUpper
    else:
        return False
    
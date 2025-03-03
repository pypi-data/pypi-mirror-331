from enum import Enum
from typing import Dict, Any
import logging

class SignalCondition(Enum):
    BUY_SIGNAL = "buy_signal"
    SELL_SIGNAL = "sell_signal"
    
def valid_signal_condition_name(condition_name) -> bool:
    return condition_name in [condition.value for condition in SignalCondition]

def check_signal_condition(condition_name: str, target_value: float, ticker_info: Dict[str, Any]) -> bool:
    logging.debug(f"Checking signal condition {condition_name}")
    volatility_analysis_buy: bool = ticker_info.get("volatility_analysis", {}).get("Buy_Signal", False)
    momentum_analysis_buy: bool = ticker_info.get("momentum_analysis", {}).get("Buy_Signal")
    volatility_analysis_sell: bool = ticker_info.get("volatility_analysis", {}).get("Sell_Signal", False)
    momentum_analysis_sell: bool = ticker_info.get("momentum_analysis", {}).get("Sell_Signal", False)
    logging.debug(f"Volatility analysis buy: {volatility_analysis_buy}, momentum analysis buy: {momentum_analysis_buy}, volatility analysis sell: {volatility_analysis_sell}, momentum analysis sell: {momentum_analysis_sell}")

    if condition_name == SignalCondition.BUY_SIGNAL.value:
        return volatility_analysis_buy or momentum_analysis_buy
    elif condition_name == SignalCondition.SELL_SIGNAL.value:
        return volatility_analysis_sell or momentum_analysis_sell
    else:
        return False
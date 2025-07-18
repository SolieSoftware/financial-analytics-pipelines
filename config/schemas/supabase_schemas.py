from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone, date
from dataclasses import dataclass


@dataclass
class RSIAnalysisResult:
    symbol: str
    date: datetime
    rsi_value: float
    open: float
    close: float
    high: float
    low: float
    volume: int = None
    rsi_period: int = 14
    created_at: datetime = None

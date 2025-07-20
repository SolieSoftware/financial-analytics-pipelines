import pandas as pd
import numpy as np
import yfinance as yf
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSIModel:
    def __init__(self, period=14):
        self.period = period
    
    def calculate_rsi(self, prices) -> pd.Series:
        """Calculate RSI for a series of prices"""
        # Calculate price changes
        delta = prices.diff()  # Computes the difference between consecutive price values
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_stock_data(self, symbol, period="1y") -> pd.DataFrame:
        """Fetch stock data"""
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    
    def analyze_stock(self, symbol) -> pd.DataFrame:
        """Complete RSI analysis for a stock"""
        # Get stock data
        data = self.get_stock_data(symbol)
        
        # Calculate RSI
        data['RSI'] = self.calculate_rsi(data['Close'])
        
        return data
    


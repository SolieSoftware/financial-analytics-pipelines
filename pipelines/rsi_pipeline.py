"""
Base pipeline class providing common functionality for all financial analytics pipelines.
"""

import logging
from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone, date
import os
from config.schemas.supabase_schemas import RSIAnalysisResult

from prefect import flow, task, get_run_logger
from utils.supabase_manager import SupabaseManager
from financial_models.rsi.model import RSIModel

logging.basicConfig(level=logging.INFO)
logger1 = logging.getLogger(__name__)


@task(name="Get Stock Symbols")
def get_us_stock_symbols():
    logger = get_run_logger()
    # Simple list of major US stocks for testing
    us_symbols = [
        "AAPL",
        "GOOGL",
        "MSFT",
        "AMZN",
        "TSLA",
        "META",
        "NVDA",
        "NFLX",
        "JPM",
        "JNJ",
        "PG",
        "UNH",
        "HD",
        "MA",
        "V",
        "PYPL",
        "BAC",
        "ADBE",
        "CRM",
        "ABT",
        "KO",
        "PEP",
        "TMO",
        "AVGO",
        "COST",
        "DHR",
        "NEE",
        "LLY",
        "ABBV",
        "TXN",
        "ACN",
        "HON",
        "VZ",
        "CMCSA",
        "ADP",
        "WMT",
    ]
    logger.info(f"Using {len(us_symbols)} US stock symbols for analysis")
    return us_symbols


@task(name="Perform RSI Analysis")
def perform_rsi_analysis(symbols: list[str]):
    logger = get_run_logger()
    rsi_model = RSIModel(period=14)

    results = {}
    errors = []

    for symbol in symbols:
        try:
            rsi_data = rsi_model.analyze_stock(symbol)
            results[symbol] = rsi_data
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            errors.append(f"{symbol}: {e}")

    return {"results": results, "errors": errors}


@task(name="Store RSI Results")
def store_rsi_results(
    supabase_manager: SupabaseManager,
    data: Dict[str, Any],
    table_name: str = "rsi_calculations",
) -> bool:
    logger = get_run_logger()
    try:
        rsi_calculations = []
        for symbol, rsi_data in data.items():
            # Get the latest values from the DataFrame
            latest_data = rsi_data.iloc[-1]

            rsi_calc = RSIAnalysisResult(
                symbol=symbol,
                date=datetime.now(),
                rsi_value=float(latest_data["RSI"]),
                rsi_period=14,
                open=float(latest_data["Open"]),
                close=float(latest_data["Close"]),
                high=float(latest_data["High"]),
                low=float(latest_data["Low"]),
                volume=int(latest_data["Volume"]),
                created_at=datetime.now(timezone.utc),
            )
            rsi_calculations.append(rsi_calc)

        # Insert all RSI calculations at once
        result = supabase_manager.batch_insert_rsi_calculations(rsi_calculations)

        if result["success"]:
            logger.info(
                f"Successfully stored {result['inserted_count']} RSI calculations"
            )
            return True
        else:
            logger.error(f"Failed to store RSI results: {result['error']}")
            return False

    except Exception as e:
        logger.error(f"Error storing RSI results: {e}")
        return False


@flow(name="RSI Analysis Pipeline")
def rsi_analysis_pipeline(
    symbols: List[str],
    period: int = 14,
    store_market_data: bool = True,
    cleanup_days: int = 30,
) -> Dict[str, Any]:
    logger = get_run_logger()
    logger.info("Starting RSI Analysis Pipeline")

    supabase_manager = SupabaseManager(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_API_KEY"),
    )

    symbols = get_us_stock_symbols()

    logger.info(f"Found {len(symbols)} total US stocks")
    logger.info(f"Starting RSI Analysis for {len(symbols)} stocks")

    response = perform_rsi_analysis(symbols)

    rsi_results = response["results"]

    store_rsi_results(supabase_manager, rsi_results)

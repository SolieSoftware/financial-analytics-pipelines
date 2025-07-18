"""
Base pipeline class providing common functionality for all financial analytics pipelines.
"""

import logging
from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone, date
import os
from config.schemas.supabase_schemas import RSIAnalysisResult

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context
from prefect.blocks.system import Secret
from pydantic import BaseModel
from us_symbols_fetcher import get_all_us_symbols
from supabase import create_client, Client
from sqlachemy import create_engine
from supabase_data_manager import SupabaseDataManager
import asyncio

from config.settings import get_settings

from financial_models.rsi.model import RSIModel



@task(name="Initialize Supabase")
def setup_supabase_connection() -> SupabaseDataManager:
    logger = get_run_logger()
    try:
        manager = SupabaseDataManager(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            database_url=os.getenv("SUPABASE_DB_NAME"),
        )
        logger.info("Supabase connection initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Supabase connection: {e}")
    return manager


@task(name="Get Stock Symbols")
def get_us_stock_symbols():
    logger = get_run_logger()
    # Comprehensive method (most complete, may take longer)
    us_symbols = get_all_us_symbols(method="comprehensive")
    logger.info(f"Found {len(us_symbols)} total US stocks")
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

    return {
        'results': results,
        'errors': errors
    }

@task(name="Store RSI Results")
def store_rsi_results(
    supabase_manager: SupabaseDataManager,
    data: Dict[str, Any],
    table_name: str = "rsi_calculations"
) -> bool:
    logger = get_run_logger()
    try:
        rsi_calculations = []
        for symbol, rsi_data in data.items():
            rsi_calc = RSIAnalysisResult(
                symbol=symbol,
                date=date.today(),
                rsi_value = rsi_data['RSI'],
                rsi_period = 14,
                open = rsi_data['Open'],
                close = rsi_data['Close'],
                high = rsi_data['High'],
                low = rsi_data['Low'],
                volume = rsi_data['Volume'],
                created_at = datetime.now(timezone.utc).isoformat()
            )
            rsi_calculations.append(rsi_calc)

            result = asyncio.run(supabase_manager.batch_insert_rsi_calculations(rsi_calculations)) 

            if result['success']:
                logger.info(f"Successfully stored {result['inserted_count']} RSI calculations")
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
    cleanup_days: int =30
) -> Dict[str, Any]:
    
    logger = get_run_logger
    logger.info("Starting RSI Analysis Pipeline")

    supabase_manager = setup_supabase_connection()

    symbols = get_us_stock_symbols()

    logger.info(f"Found {len(symbols)} total US stocks")
    logger.info(f"Starting RSI Analysis for {len(symbols)} stocks")

    response = perform_rsi_analysis(symbols)

    rsi_results = response['results']

    store_rsi_results(supabase_manager, rsi_results)
        
            




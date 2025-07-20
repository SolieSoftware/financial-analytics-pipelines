from typing import Any, Dict, Optional, List, Union
from datetime import datetime, timezone, date
import logging
from supabase import create_client, Client
from config.schemas.supabase_schemas import RSIAnalysisResult


class SupabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client = create_client(supabase_url, supabase_key)
        self.logger = logging.getLogger(__name__)
        self.rsi_table_name = "rsi_calculations"

    def validate_rsi_data(self, data: List[RSIAnalysisResult]) -> bool:
        """Validate RSI data against the schema"""
        required_fields = [
            "symbol",
            "date",
            "rsi_value",
            "open",
            "close",
            "high",
            "low",
        ]

        for item in data:
            # Check if it's a dataclass instance
            if not isinstance(item, RSIAnalysisResult):
                self.logger.error(f"Invalid data type: {type(item)}")
                return False

            # Check required fields
            for field in required_fields:
                if not hasattr(item, field) or getattr(item, field) is None:
                    self.logger.error(
                        f"Missing required field '{field}' for symbol: {item.symbol}"
                    )
                    return False

        return True

    def batch_insert_rsi_calculations(
        self, rsi_data_list: List[RSIAnalysisResult]
    ) -> Dict[str, Any]:
        """Insert RSI data into the database"""
        try:
            # Debug: Print the first item to see its structure
            if rsi_data_list:
                first_item = rsi_data_list[0]
                print(f"Debug - First item type: {type(first_item)}")
                print(f"Debug - First item created_at: {first_item.created_at}")
                print(
                    f"Debug - First item created_at type: {type(first_item.created_at)}"
                )
            data_list = [
                {
                    "symbol": rsi_data.symbol,
                    "date": rsi_data.date.isoformat(),
                    "rsi_value": round(float(rsi_data.rsi_value), 4),
                    "rsi_period": 14,
                    "open": round(float(rsi_data.open), 4),
                    "close": round(float(rsi_data.close), 4),
                    "high": round(float(rsi_data.high), 4),
                    "low": round(float(rsi_data.low), 4),
                    "volume": int(rsi_data.volume)
                    if rsi_data.volume is not None
                    else None,
                    "created_at": (
                        rsi_data.created_at.isoformat()
                        if rsi_data.created_at is not None
                        else datetime.now(timezone.utc).isoformat()
                    ),
                }
                for rsi_data in rsi_data_list
            ]

            # Validate the original dataclass objects, not the converted dict
            if not self.validate_rsi_data(rsi_data_list):
                self.logger.error("Invalid RSI data format")
                return {"success": False, "error": "Invalid RSI data format"}

            response = (
                self.client.table(self.rsi_table_name).insert(data_list).execute()
            )
            return {"success": True, "inserted_count": len(data_list)}
        except Exception as e:
            logging.error(f"Error inserting RSI data: {e}")
            return {"success": False, "error": str(e)}

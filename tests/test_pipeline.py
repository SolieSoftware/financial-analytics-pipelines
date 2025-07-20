#!/usr/bin/env python3
"""
Test script to run the RSI pipeline and check if it works.
"""

import os
from dotenv import load_dotenv
from pipelines.rsi_pipeline import rsi_analysis_pipeline


def main():
    # Load environment variables
    load_dotenv()

    print("🚀 Starting RSI Pipeline Test...")
    print(f"Supabase URL: {os.getenv('SUPABASE_URL', 'Not set')}")
    print(f"Supabase Key: {'Set' if os.getenv('SUPABASE_KEY') else 'Not set'}")

    try:
        # Run the pipeline with a small test
        print("\n📊 Running RSI Analysis Pipeline...")
        result = rsi_analysis_pipeline(
            symbols=["AAPL", "GOOGL", "MSFT"],  # Test with just 3 symbols
            period=14,
            store_market_data=True,
        )

        print(f"\n✅ Pipeline completed successfully!")
        print(f"Result: {result}")

    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

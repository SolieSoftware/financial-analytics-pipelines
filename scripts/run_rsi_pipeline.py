# run_rsi_pipeline.py
import asyncio
from pipelines.rsi_pipeline import rsi_analysis_pipeline

if __name__ == "__main__":
    result = rsi_analysis_pipeline()
    print(f"Pipeline completed: {result}")
# Financial Analytics Pipelines Documentation

## Overview

This documentation provides comprehensive information about the Financial Analytics Pipelines project, which uses Prefect for workflow orchestration to process and analyze financial market data.

## Table of Contents

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Pipelines](#pipelines)
6. [Development](#development)
7. [Deployment](#deployment)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## Architecture

### System Components

The financial analytics pipeline system consists of the following components:

- **Prefect Server**: Workflow orchestration and monitoring
- **PostgreSQL Database**: Data storage and persistence
- **Redis**: Caching and state management
- **Python Pipelines**: Core data processing logic
- **Docker**: Containerization for deployment
- **Grafana**: Monitoring and visualization

### Data Flow

```
Financial APIs → Data Ingestion → Data Validation → Processing → Analysis → Storage → Monitoring
```

### Pipeline Architecture

Each pipeline follows the ETL (Extract, Transform, Load) pattern:

1. **Extract**: Fetch data from financial APIs (Yahoo Finance, Alpha Vantage)
2. **Transform**: Clean, validate, and calculate financial metrics
3. **Load**: Store processed data in PostgreSQL database
4. **Validate**: Ensure data quality and completeness

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (for containerized deployment)
- Git

### Local Development Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd financial-analytics-pipelines
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Prefect**:
   ```bash
   prefect server start
   ```

### Docker Setup

1. **Build and run with Docker Compose**:

   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Access services**:
   - Prefect UI: http://localhost:4201
   - PostgreSQL: localhost:5432
   - Grafana: http://localhost:3000

## Configuration

### Environment Variables

Key configuration variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/financial_analytics

# API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
QUANDL_API_KEY=your_key_here

# Prefect
PREFECT_API_URL=http://localhost:4200/api

# Data Storage
DATA_STORAGE_PATH=./data
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed

# Logging
LOG_LEVEL=INFO
```

### Database Schema

The system uses the following main tables:

- `market_data`: Raw market data from APIs
- `financial_analysis`: Calculated financial metrics
- `pipeline_runs`: Pipeline execution history

## Usage

### Running Pipelines

#### Using Python Scripts

```python
from pipelines.market_data_ingestion import market_data_ingestion_flow
from pipelines.financial_analysis import financial_analysis_flow

# Run market data ingestion
result = market_data_ingestion_flow(["AAPL", "GOOGL", "MSFT"])

# Run financial analysis
result = financial_analysis_flow(["AAPL", "GOOGL", "MSFT"])
```

#### Using Shell Scripts

```bash
# Run market data ingestion
./scripts/run_pipeline.sh -p market_data_ingestion -s AAPL,GOOGL,MSFT

# Run financial analysis
./scripts/run_pipeline.sh -p financial_analysis -s AAPL,GOOGL,MSFT
```

#### Using Docker

```bash
# Run with Docker Compose
cd docker
docker-compose up pipeline

# Run individual pipeline
docker run --env-file .env financial-analytics-pipeline
```

### Prefect UI

Access the Prefect UI at http://localhost:4201 to:

- Monitor pipeline runs
- View flow logs
- Manage deployments
- Configure schedules

## Pipelines

### Market Data Ingestion Pipeline

**Purpose**: Extract market data from multiple financial APIs

**Features**:

- Multi-source data extraction (Yahoo Finance, Alpha Vantage)
- Data validation and quality checks
- Automatic retry mechanisms
- Real-time monitoring

**Configuration**:

```python
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
result = market_data_ingestion_flow(symbols)
```

### Financial Analysis Pipeline

**Purpose**: Calculate financial metrics and technical indicators

**Features**:

- Technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands)
- Risk metrics (Volatility, VaR, Drawdown)
- Performance metrics (Returns, Sharpe Ratio, Calmar Ratio)
- Comprehensive data validation

**Configuration**:

```python
symbols = ["AAPL", "GOOGL", "MSFT"]
result = financial_analysis_flow(symbols)
```

## Development

### Project Structure

```
financial-analytics-pipelines/
├── pipelines/           # Pipeline definitions
│   ├── __init__.py
│   ├── base.py         # Base pipeline class
│   ├── market_data_ingestion.py
│   └── financial_analysis.py
├── config/             # Configuration
│   ├── __init__.py
│   └── settings.py
├── utils/              # Utilities
│   ├── __init__.py
│   ├── database.py
│   └── data_validation.py
├── tests/              # Test suite
├── docker/             # Docker configurations
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── data/               # Data storage
```

### Adding New Pipelines

1. **Create pipeline class**:

   ```python
   from pipelines.base import BasePipeline, PipelineConfig

   class MyNewPipeline(BasePipeline):
       def __init__(self):
           config = PipelineConfig(
               name="my_new_pipeline",
               description="Description of my pipeline",
               version="1.0.0"
           )
           super().__init__(config)

       def validate_inputs(self, **kwargs) -> bool:
           # Input validation logic
           pass

       def extract(self, **kwargs):
           # Data extraction logic
           pass

       def transform(self, data, **kwargs):
           # Data transformation logic
           pass

       def load(self, data, **kwargs) -> bool:
           # Data loading logic
           pass

       def validate_outputs(self, **kwargs) -> bool:
           # Output validation logic
           pass
   ```

2. **Create Prefect flow**:

   ```python
   @flow(name="my-new-pipeline")
   def my_new_pipeline_flow(**kwargs):
       pipeline = MyNewPipeline()
       return execute_pipeline(pipeline, **kwargs)
   ```

3. **Add tests**:
   ```python
   def test_my_new_pipeline():
       pipeline = MyNewPipeline()
       # Add test cases
   ```

### Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_market_data_ingestion.py

# Run with coverage
pytest --cov=pipelines --cov-report=html
```

### Code Quality

Use the provided tools for code quality:

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Deployment

### Production Deployment

1. **Environment Setup**:

   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DATABASE_URL=postgresql://prod_user:prod_pass@prod_host:5432/financial_analytics
   ```

2. **Database Migration**:

   ```bash
   # Run database migrations
   alembic upgrade head
   ```

3. **Deploy with Docker**:
   ```bash
   cd docker
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Monitoring

#### Prefect Monitoring

- **Flow Runs**: Monitor pipeline execution
- **Task States**: Track individual task performance
- **Logs**: View detailed execution logs
- **Metrics**: Performance and error metrics

#### Database Monitoring

```sql
-- Check recent pipeline runs
SELECT * FROM pipeline_runs
WHERE created_at >= NOW() - INTERVAL '1 day'
ORDER BY created_at DESC;

-- Check data quality
SELECT
    symbol,
    COUNT(*) as record_count,
    COUNT(CASE WHEN close IS NULL THEN 1 END) as null_closes
FROM market_data
WHERE ingestion_timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY symbol;
```

#### Grafana Dashboards

Set up Grafana dashboards for:

- Pipeline execution metrics
- Database performance
- Data quality indicators
- System resource usage

## Troubleshooting

### Common Issues

#### Pipeline Failures

1. **API Rate Limits**:

   - Implement exponential backoff
   - Use multiple API keys
   - Add delays between requests

2. **Database Connection Issues**:

   - Check database URL
   - Verify network connectivity
   - Check connection pool settings

3. **Data Quality Issues**:
   - Review validation logs
   - Check data source availability
   - Verify data format changes

#### Performance Issues

1. **Slow Pipeline Execution**:

   - Optimize database queries
   - Use parallel processing
   - Implement caching

2. **Memory Issues**:
   - Process data in batches
   - Use streaming for large datasets
   - Monitor memory usage

### Debugging

#### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
```

#### Check Prefect Logs

```bash
# View flow run logs
prefect flow-run logs <flow-run-id>

# View task logs
prefect task-run logs <task-run-id>
```

#### Database Debugging

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'market_data';

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;
```

### Support

For issues and questions:

1. Check the logs in `logs/` directory
2. Review Prefect UI for flow run details
3. Check database connection and data quality
4. Verify environment configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

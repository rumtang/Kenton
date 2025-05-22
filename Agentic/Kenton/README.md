# Kenton Deep Research Agent

A strategic research agent with real-time data access through MCP tools and comprehensive financial market insights.

## Current Architecture

### Core Files
- `main.py` - CLI interface for the research agent
- `run.py` - Clean environment launcher
- `agent_config.py` - Agent configuration with MCP tools
- `truly_simple_api.py` - Simple API server for frontend
- `consulting_brain_apis.mcp` - Core MCP tool configuration
- `fmp_apis.mcp` - Financial Modeling Prep API configuration

### Financial Data Integration
- `tools/fmp_api_tools.py` - Financial Modeling Prep integration module
- `tools/mcp_api_loader.py` - MCP configuration loader
- `tools/simple_mcp_wrapper.py` - MCP tool wrapper

### Tools
- `tools/` - Research and API tools
  - Standard tools: summarize, compare_sources, report_generator, etc.
  - Financial tools: company profiles, financial statements, market data, etc.

### Frontend
- `frontend/` - Next.js web interface
  - `components/SimpleResearchApp.tsx` - Main UI component
  - `app/page.tsx` - Landing page

### Scripts
- `start_backend.sh` - Start backend service
- `start_all.sh` - Start all services
- `stop_all.sh` - Stop all services

## Running the System

1. **CLI Mode**: `poetry run python run.py`
2. **Web Interface**: 
   - Backend: `./start_backend.sh`
   - Frontend: `cd frontend && npm run dev`
   - Or all at once: `./start_all.sh`

## Configuration

Environment variables in `.env`:
- `OPENAI_API_KEY` - Required
- `MARKET_DATA_KEY` - FMP API key (required for financial data)
- `FMP_CONFIG_PATH` - Path to FMP configuration (default: ./fmp_apis.mcp)
- Additional API keys for various services (NEWS_API_KEY, etc.)

## Financial Data Capabilities

The agent has comprehensive financial data capabilities through the Financial Modeling Prep API integration:

- **Company Data**: Profiles, financial statements, key metrics
- **Market Data**: Real-time quotes, historical prices
- **News & Analysis**: Company-specific and general market news
- **Financial Ratios**: Profitability, liquidity, solvency metrics

### Available Financial API Endpoints

- `FMPCompanyProfile` - Detailed company information
- `FMPIncomeStatement` - Revenue, expenses, profitability data
- `FMPBalanceSheet` - Assets, liabilities, equity breakdown
- `FMPCashFlow` - Cash flow analysis
- `FMPKeyMetrics` - Performance indicators
- `FMPFinancialRatios` - Financial health metrics
- `FMPStockPrice` - Current stock quotes
- `FMPHistoricalPrice` - Historical price data
- `FMPStockNews` - Company-specific news
- `FMPMarketNews` - General market news

## Testing Financial Integration

To test the FMP API integration:

```bash
python -m tools.fmp_api_tools
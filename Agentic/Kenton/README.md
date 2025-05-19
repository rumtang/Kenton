# Kenton Deep Research Agent

A strategic research agent with real-time data access through MCP tools.

## Current Architecture

### Core Files
- `main.py` - CLI interface for the research agent
- `run.py` - Clean environment launcher
- `agent_config.py` - Agent configuration with MCP tools
- `truly_simple_api.py` - Simple API server for frontend
- `consulting_brain_apis.mcp` - MCP tool configuration

### Frontend
- `frontend/` - Next.js web interface
  - `components/SimpleResearchApp.tsx` - Main UI component
  - `app/page.tsx` - Landing page

### Tools
- `tools/` - Research and API tools
  - `simple_mcp_wrapper.py` - MCP tool wrapper
  - `mcp_api_loader.py` - MCP configuration loader
  - Standard tools: summarize, compare_sources, report_generator, etc.

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
- API keys for various services (NEWS_API_KEY, etc.)

## Archived Files

See `Misc/` folder for deprecated scripts, tests, and old implementations.
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

### Environment Variables in `.env`:
- `OPENAI_API_KEY` - Required
- `OPENAI_VECTOR_STORE_ID` - Required for file search functionality
- API keys for various services (NEWS_API_KEY, etc.)

## API Integration Standards
This project strictly adheres to the following integration standards:

1. **OpenAI SDK Only**: All API integrations must use the OpenAI SDK (≥1.30)
2. **Consistent Agent Configuration**: Both CLI and web interfaces must use identical agent configurations
3. **Direct Agent Access**: Frontend must directly access the same agent implementation as the CLI
4. **OpenAI LLM API Only**: All LLM, search, and vector database functionality must use OpenAI APIs only (never use Anthropic/Claude or other LLM providers)
5. **CLI-Web Equivalence**: Research from CLI or web must produce identical outputs with identical settings

### Vector Store / File Search Configuration
To use file search functionality:
1. Create a vector store in the OpenAI dashboard
2. Add the vector store ID to your `.env` file as `OPENAI_VECTOR_STORE_ID`
3. Upload your files to the vector store
4. Use the `file_search` tool in your agent queries

### API Error Handling
All tools implement diagnostic-rich error codes with detailed information:
- Error code format: `ERROR-XX000`
- Each error includes:
  - Problem description
  - Context explaining what went wrong
  - Solution steps to resolve the issue
  - Technical details for debugging

## Archived Files

See `Misc/` folder for deprecated scripts, tests, and old implementations.
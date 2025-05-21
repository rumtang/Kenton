# API Integration Guide

This guide explains how to integrate new APIs into the Deep Research Agent system after the removal of the Model Control Panel (MCP) infrastructure.

## Overview

The system now provides a clean, lightweight framework for integrating external APIs without MCP dependencies. The architecture uses the OpenAI Agents SDK directly with function tools for integrating APIs.

## Core Components

### 1. API Tool Template

The `tools/api_tool_template.py` file provides a complete framework for creating new API integrations, including:

- Error handling with rich diagnostics
- Retry logic for resilient API calls
- Input validation
- Response formatting
- Environment variable management

### 2. Agent Configuration

The `agent_config.py` file contains the central integration point for registering API tools:

```python
def get_api_tools():
    """
    Load API tools from the tools directory.
    This function serves as an extension point for adding new API integrations.
    
    Returns:
        List of API tool functions compatible with OpenAI Agents SDK
    """
    api_tools = []
    
    # Import available API tools
    try:
        from tools.weather_api import weather_api
        api_tools.append(weather_api)
        logger.info("Added weather API tool")
    except ImportError:
        logger.warning("Weather API tool not available")
    
    # Add other API tools here
    
    logger.info(f"Loaded {len(api_tools)} API tools")
    return api_tools
```

### 3. API Server

The `fixed_api_server.py` file provides a FastAPI server that exposes the agent's capabilities via RESTful endpoints, including:

- Streaming responses for real-time feedback
- Health checks that show available tools
- Environment variable validation and cleanup

## Adding a New API

To add a new API integration, follow these steps:

1. Create a new file in the `tools/` directory (e.g., `tools/news_api.py`)
2. Use the API tool template structure as a starting point
3. Implement your API-specific logic
4. Register the tool in `agent_config.py`

### Example: News API Integration

```python
# tools/news_api.py
from tools.api_tool_template import function_tool, with_retry, format_response

@function_tool
@with_retry(max_retries=2)
def news_api(query: str, limit: int = 5):
    """Search for news articles on a topic."""
    # Implementation goes here
    # ...
    return format_response(data)
```

```python
# In agent_config.py, add:
try:
    from tools.news_api import news_api
    api_tools.append(news_api)
    logger.info("Added news API tool")
except ImportError:
    logger.warning("News API tool not available")
```

## Environment Configuration

API keys are stored in the `.env` file. Each API should have its own key:

```
OPENAI_API_KEY=sk-...
WEATHER_API_KEY=...
NEWS_API_KEY=...
```

The system automatically loads and validates these keys when tools are initialized.

## Error Handling

The system provides a standardized error handling framework in `tools/errors.py`:

- `AgentExecutionError` - Base class for all agent errors
- `create_api_key_error()` - Creates errors for API key issues
- `create_network_error()` - Creates errors for network connectivity issues

## Testing

Each API integration should have corresponding tests in the `tests/` directory. The testing framework supports:

- Unit tests with mocked responses
- Integration tests with real API calls (when keys are available)
- Error condition testing

## Best Practices

1. **Always validate inputs** before making API calls
2. **Handle rate limiting** with appropriate retry logic
3. **Format responses consistently** using the provided formatters
4. **Document parameters** for proper LLM tool selection
5. **Keep API tools focused** on a single responsibility
6. **Use environment variables** for all secrets and configuration

## Example API Tools

The repository includes example implementations:

- `weather_api.py` - Weather information using weatherapi.com
- `api_tool_template.py` - Complete template for creating new tools

## Extending the System

The architecture is designed to be extended with:

1. **Additional API tools** - Add more API integrations
2. **Custom response formatters** - Create domain-specific formatters
3. **Enhanced validation** - Add more sophisticated input validation
4. **Tool selection guidance** - Update agent instructions for new tools
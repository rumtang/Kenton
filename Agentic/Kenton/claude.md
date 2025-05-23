# Kenton Deep Research Agent - Technical Documentation

## Overview
The Kenton Deep Research Agent is a strategic research assistant built with OpenAI Agents SDK, designed to help business executives understand how technological and market trends impact their organizations.

## Models Available (As of May 2025)
The system uses the following OpenAI models (released after standard knowledge cutoffs):
- **gpt-4.1**: Main reasoning model for complex analysis and strategic insights
- **gpt-4.1-mini**: Lightweight model for simple queries and tool routing
- **gpt-4o-mini**: Alternative lightweight model (as referenced in CLAUDE.md)
- **text-embedding-3-large**: For vector search and semantic knowledge retrieval

Note: Additional models like o1-preview and o3 series may be available but are not currently configured in the system.

## Architecture

### Core Components
- **Agent Core**: OpenAI Agents SDK with strategic advisory instructions
- **MCP Tools**: Real-time API access (weather, news, financial data)
- **Session Management**: Conversation memory and context
- **Date Awareness**: Current date/quarter/fiscal year context
- **Enhanced CLI**: Continuous conversation interface
- **Web Interface**: Frontend matching CLI capabilities

### Key Files Structure
```
Kenton/
├── agent_config.py              # Core agent configuration
├── run.py                       # Enhanced CLI interface
├── consulting_brain_apis.mcp    # API tool configuration
├── tools/
│   ├── enhanced_mcp_wrapper.py  # Enhanced MCP integration
│   ├── simple_mcp_wrapper.py    # Fallback MCP wrapper
│   └── [other tools...]
├── frontend/                    # Web interface
└── claude.md                   # This documentation
```

## MCP Integration Solutions & Troubleshooting

### Common Issues & Solutions

#### Issue 1: Tool Selection Problems
**Problem**: Agent has tools available but chooses wrong ones (e.g., using GDELT for weather queries instead of WeatherAPI)

**Root Cause**: Insufficient tool selection guidance in agent instructions

**Solution Applied**:
1. **Enhanced Tool Selection Instructions**: Added explicit tool selection rules
2. **Priority-Based Tool Selection**: Implemented tool selection priority system
3. **Query Type Detection**: Clear query type → tool mapping

**Implementation**:
```python
# In agent_config.py instructions:
CRITICAL TOOL SELECTION RULES:

1. WEATHER QUERIES → ALWAYS use WeatherAPI tool
2. NEWS QUERIES → Use NewsAPI or TavilyAPI  
3. FINANCIAL DATA → Use MarketDataAPI/YahooFinanceAPI
4. Match query type to most specific tool first
```

#### Issue 2: Parameter Mapping Issues
**Problem**: MCP wrapper not passing parameters correctly to APIs, causing tool failures

**Root Cause**: Parameter naming inconsistencies between agent calls and API expectations

**Solution Applied**:
1. **Enhanced Parameter Processing**: Intelligent parameter mapping in MCP wrapper
2. **Common Parameter Normalization**: Convert common parameter names automatically
3. **Parameter Validation**: Validate parameters before API calls

**Implementation**:
```python
# Enhanced parameter processing in enhanced_mcp_wrapper.py:
for key, value in kwargs.items():
    if key.lower() in ['query', 'q', 'search']:
        query_params['q'] = str(value).strip()
    elif key.lower() in ['location', 'city', 'place']:
        query_params['q'] = str(value).strip()  # For weather API
    elif key.lower() in ['symbol', 'ticker']:
        query_params['symbol'] = str(value).strip().upper()
```

#### Issue 3: OpenAI SDK Tool Integration Errors
**Problem**: Multiple integration issues with OpenAI Agents SDK
- 'function' object has no attribute 'name' error
- Pydantic schema validation errors (additionalProperties must be False)
- Tool calling convention mismatches (positional vs keyword arguments)

**Root Cause**: OpenAI Agents SDK has strict requirements for tool integration

**Solution Applied**:
1. **Proper FunctionTool Creation**: All tools wrapped as FunctionTool objects
2. **Correct Schema Format**: additionalProperties set to False
3. **Calling Convention Wrapper**: Handle both positional and keyword arguments

**Implementation**:
```python
# Create wrapper for proper calling convention:
async def tool_wrapper(context, arguments):
    """Wrapper to handle async/sync and argument passing"""
    kwargs = {}
    if isinstance(arguments, dict):
        kwargs = arguments
    elif hasattr(arguments, '__dict__'):
        kwargs = arguments.__dict__
    return api_function(**kwargs)

# Create FunctionTool with correct schema:
tool = FunctionTool(
    name=api_function.__name__,
    description=description,
    params_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False  # Required by OpenAI SDK
    },
    on_invoke_tool=tool_wrapper
)
```

#### Issue 4: Tavily API Integration
**Problem**: Tavily API returning "405: Method Not Allowed" errors

**Root Cause**: Tavily requires POST requests with JSON body, not GET requests

**Solution Applied**:
1. **POST Request Support**: Modified enhanced_mcp_wrapper to use POST for Tavily
2. **JSON Body Format**: Convert query parameters to JSON body
3. **Proper Authentication**: API key passed in JSON body, not headers

**Implementation**:
```python
# Special handling for Tavily API:
if name.lower() == "tavilyapi":
    json_body = {
        'query': query_params.get('q', ''),
        'search_depth': 'basic',
        'max_results': 5,
        'api_key': api_key  # Tavily expects key in body
    }
    response = requests.post(endpoint, json=json_body, timeout=30)
```

#### Issue 5: Session Memory Not Working
**Problem**: Agent doesn't remember previous conversation context

**Root Cause**: Session context not prominently featured in agent instructions

**Solution Applied**:
```python
# Enhanced session context in agent instructions:
CONVERSATION HISTORY & CONTEXT:
{f"""
IMPORTANT: You are continuing a conversation. Here's what we've discussed recently:

{session_context}

Pay close attention to this context. When the user says "they", "their", "it", "this company", etc., 
refer back to the companies, topics, or subjects mentioned above.
""" if session_context else "This is the start of a new research session."}
```

### Prevention Checklist

#### Before Deployment:
- [ ] Test all MCP tools individually with sample parameters
- [ ] Verify tool selection logic with various query types
- [ ] Check parameter mapping for each API endpoint
- [ ] Test schema validation with OpenAI Agents SDK
- [ ] Validate API keys and authentication methods
- [ ] Test session memory with multi-turn conversations

#### Testing Commands:
```bash
# Test enhanced MCP tools loading
python -c "from tools.enhanced_mcp_wrapper import get_enhanced_mcp_tools; tools = get_enhanced_mcp_tools(); print(f'Loaded {len(tools)} tools')"

# Test specific tools
python -c "from tools.enhanced_mcp_wrapper import EnhancedAPIManager; manager = EnhancedAPIManager(); print(manager.test_tool('WeatherAPI', q='Chicago'))"

# Test Tavily search
python -c "from tools.enhanced_mcp_wrapper import EnhancedAPIManager; manager = EnhancedAPIManager(); print(manager.test_tool('TavilyAPI', query='latest AI developments 2024')[:500])"

# Test agent tool selection
poetry run python run.py
# Then test: "What's the weather in Chicago?"
# And test: "Search for recent news about Tesla"
```

### Monitoring & Maintenance

#### Log Monitoring:
Watch for these log patterns indicating issues:
- `⚠️ Weather tool not being selected`
- `❌ Parameter mapping failed`
- `🔧 Schema validation error`
- `✅ Enhanced MCP tools loaded` (success indicator)

#### Regular Health Checks:
1. **Daily**: Test key weather and news tools
2. **Weekly**: Test financial tool endpoints and session memory
3. **Monthly**: Review tool usage statistics and selection accuracy
4. **Quarterly**: Update API endpoints and authentication methods

## Date Awareness Implementation

### Features
- **Current Date Context**: Agent knows current date, day, quarter
- **Fiscal Year Awareness**: FY2025 (Oct-Sep cycle)
- **Earnings Season Detection**: Knows Jan, Apr, Jul, Oct are earnings months
- **Market Hours**: Considers 9:30 AM - 4:00 PM EST trading hours

### Implementation
```python
def get_current_date_context():
    """Generate current date context for agent instructions."""
    now = datetime.now()
    current_date = now.strftime("%B %d, %Y")
    current_quarter = f"Q{(now.month-1)//3 + 1}"
    # Calculate fiscal year (October 1 start)
    fiscal_year = current_year + 1 if now.month >= 10 else current_year
    return {
        "current_date": current_date,
        "current_quarter": current_quarter,
        "fiscal_year": fiscal_year,
        # ... other context
    }
```

## Enhanced CLI Features

### Continuous Conversation
- No restart required after each query
- Session memory maintains context
- Natural conversation flow

### Commands Available
- `/help` - Show all commands
- `/thinking` - Toggle thinking display
- `/model` - Switch between models  
- `/session` - View session info
- `/clear` - Start fresh session
- `/quit` - Exit cleanly

### Thinking Display
- Shows agent reasoning process
- "Analyzing query and selecting appropriate tools..."
- "Executing research plan..."
- Can be toggled on/off

## File Locations & Backups

### Key Files:
- **MCP Configuration**: `./consulting_brain_apis.mcp`
- **Enhanced Wrapper**: `./tools/enhanced_mcp_wrapper.py`
- **Agent Configuration**: `./agent_config.py`
- **CLI Interface**: `./run.py`

### Environment Variables Required:
```bash
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_weather_key  
NEWS_API_KEY=your_news_key
TAVILY_API_KEY=your_tavily_key
# ... other API keys
```

## Emergency Procedures

### If MCP Tools Completely Fail:
1. **Fallback to Tavily**: Agent can still function with TavilyAPI for research
2. **Simple Wrapper Fallback**: Enhanced wrapper falls back to simple wrapper
3. **Manual Tool Disable**: Comment out MCP tools in agent_config.py

### Recovery Steps:
```bash
# 1. Check API connectivity
curl -H "key: $WEATHER_API_KEY" "https://api.weatherapi.com/v1/current.json?q=Chicago&key=$WEATHER_API_KEY"

# 2. Test enhanced MCP tools
python tools/enhanced_mcp_wrapper.py

# 3. Restart agent
poetry run python run.py
```

### Debugging Commands:
```bash
# Test tool loading
python -c "from agent_config import get_agent; agent = get_agent(); print(f'Tools: {len(agent.tools)}')"

# Test session management
python -c "from agent_config import session_manager; session = session_manager.get_session('test'); print(session)"

# Check date awareness
python -c "from agent_config import get_current_date_context; print(get_current_date_context())"
```

## Version History

### v3.0 (Current - Priority 3 Complete)
- ✅ Enhanced CLI with continuous conversation
- ✅ Session memory and context management
- ✅ Thinking display and CLI commands
- ✅ Enhanced MCP wrapper with better tool selection
- ✅ Comprehensive error handling and fallbacks

### v2.1 (Priority 2 Complete)
- ✅ Tavily integration for enhanced search
- ✅ Better tool selection logic
- ✅ Enhanced parameter mapping

### v2.0 (Priority 1 Complete)
- ✅ Date awareness implementation
- ✅ Current quarter and fiscal year context
- ✅ Time-sensitive data handling

### v1.0 (Initial)
- Basic MCP tool integration
- Simple agent configuration
- Core functionality established

## Future Enhancements (Roadmap)

### Priority 4: Frontend Parity
- [ ] Web interface matching CLI capabilities
- [ ] Session management in web UI
- [ ] Thinking display in browser
- [ ] Real-time streaming responses

### Priority 5: Multi-Model Layer
- [ ] Task-based model selection
- [ ] Cost optimization through model routing
- [ ] Performance optimization

## Support & Troubleshooting

### For Issues:
1. Check this documentation first
2. Review log files for specific error patterns
3. Test individual tool endpoints manually
4. Use debugging commands provided above

### Contact Information:
- Project: Kenton Deep Research Agent
- Documentation: claude.md
- Last Updated: May 22, 2025

## Recent Fixes (May 22, 2025)

### Fixed Issues:
1. **Tavily API Integration** - Now properly using POST requests with JSON body
2. **Tool Wrapping Errors** - All tools properly wrapped as FunctionTool objects
3. **Schema Validation** - additionalProperties correctly set to False
4. **Parameter Handling** - Enhanced wrapper handles both positional and keyword arguments

### Current Status:
- ✅ All 14 tools loading successfully (including 10 MCP tools)
- ✅ Tavily search working for real-time web queries
- ✅ Weather, News, and Financial APIs operational
- ✅ Web interface functional at http://localhost:3000
- ✅ Backend API stable at http://localhost:8001

### Known Limitations:
- File search tool has issues with 'tool_resources' parameter
- Some API keys not configured (CompanyInfoAPI, IndustryReportsAPI)
- Yahoo Finance API returns 403 (may need valid API key)
- **Tool Parameter Passing Issue**: The agent sometimes calls tools without required parameters
  - This happens when the agent doesn't understand what parameters each tool expects
  - Solution: Parameter schemas have been added to guide the agent
  - Workaround: Be explicit in queries (e.g., "Search for 'Microsoft AI' using TavilyAPI")

### Debugging Tool Issues:

To test if tools are working correctly:

```bash
# Test Tavily directly
python3 -c "
from tools.enhanced_mcp_wrapper import EnhancedAPIManager
manager = EnhancedAPIManager()
print(manager.test_tool('tavilyapi', query='Microsoft AI strategy'))
"

# Test FMP directly  
python3 -c "
from tools.enhanced_mcp_wrapper import EnhancedAPIManager
manager = EnhancedAPIManager()
print(manager.test_tool('marketdataapi', symbol='MSFT'))
"
```

### Tool Usage Tips:

1. **Be Explicit**: Instead of "analyze Microsoft", say "Get MSFT stock data and search for Microsoft AI initiatives"
2. **Specify Tools**: Mention tool names when possible (e.g., "Use TavilyAPI to search...")
3. **Include Parameters**: Mention what to search for or what stock symbol to use
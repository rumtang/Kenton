# Enhanced agent configuration with date awareness, session management, and improved tool selection

from agents import Agent, ModelSettings, WebSearchTool, FileSearchTool
from tools.summarize import summarize
from tools.compare_sources import compare_sources
from tools.report_generator import generate_report
from tools.file_search import file_search
from tools.mcp_api_loader import APIManager
from dotenv import load_dotenv
import os
from datetime import datetime, date
import calendar

# Load environment variables from .env file
load_dotenv()

def get_current_date_context():
    """Generate current date context for agent instructions."""
    now = datetime.now()
    current_date = now.strftime("%B %d, %Y")
    current_day = now.strftime("%A")
    current_month = now.strftime("%B")
    current_year = now.year
    current_quarter = f"Q{(now.month-1)//3 + 1}"
    
    # Calculate fiscal year (assuming October 1 start)
    if now.month >= 10:
        fiscal_year = current_year + 1
    else:
        fiscal_year = current_year
    
    return {
        "current_date": current_date,
        "current_day": current_day,
        "current_month": current_month,
        "current_year": current_year,
        "current_quarter": current_quarter,
        "fiscal_year": fiscal_year,
        "timestamp": now.isoformat()
    }

def select_model_for_task(query_type="general"):
    """Select appropriate model based on task complexity."""
    model_mapping = {
        "financial": "gpt-4.1",      # Complex financial analysis
        "research": "gpt-4.1",       # Deep research tasks
        "summary": "gpt-4.1-mini",   # Simple summarization
        "weather": "gpt-4.1-mini",   # Simple API calls
        "general": "gpt-4.1"         # Default to full model
    }
    return model_mapping.get(query_type, "gpt-4.1")

def get_agent(model="gpt-4.1", session_context=None, enable_reasoning=False):
    """
    Returns a configured Deep Research agent with:
    - Research-focused instructions
    - Model settings for consistency
    - Tools for research capabilities
    - Date awareness for financial queries
    - Session memory capability
    - Enhanced tool selection
    """
    
    # Get current date context
    date_context = get_current_date_context()
    
    # Build tools list based on model capabilities
    if model in ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"]:
        # o3 and 4.1 models support function tools
        tools = [
            summarize,
            compare_sources,
            generate_report,
            file_search  # Add file search as function tool
        ]
    else:
        tools = [
            WebSearchTool(),
            summarize,
            compare_sources,
            generate_report
        ]
        
        # Add FileSearchTool if vector store ID is configured (for non-o3 models)
        from tools.vector_search import get_file_search_tool
        file_search_tool = get_file_search_tool()
        if file_search_tool:
            tools.append(file_search_tool)
    
    # Load MCP API tools with enhanced wrapper
    try:
        mcp_path = os.getenv("MCP_CONFIG_PATH", "./consulting_brain_apis.mcp") 
        if os.path.exists(mcp_path):
            # Use enhanced MCP wrapper
            from tools.enhanced_mcp_wrapper import get_enhanced_mcp_tools
            wrapped_tools = get_enhanced_mcp_tools(mcp_path)
            tools.extend(wrapped_tools)
            print(f"✅ Loaded {len(wrapped_tools)} enhanced API tools from {mcp_path}")
    except Exception as e:
        print(f"⚠️ Failed to load enhanced MCP tools: {e}")
        # Fallback to simple wrapper if enhanced fails
        try:
            from tools.simple_mcp_wrapper import get_mcp_tools
            wrapped_tools = get_mcp_tools(mcp_path)
            tools.extend(wrapped_tools)
            print(f"✅ Loaded {len(wrapped_tools)} API tools from {mcp_path} (fallback)")
        except Exception as e2:
            print(f"❌ Failed to load any MCP tools: {e2}")
    
    # Build enhanced instructions with date awareness and tool selection guidance
    date_aware_instructions = f"""
You are a strategic advisor who helps business executives understand how technological and market trends actually impact their organizations. Your analysis should be immediately actionable in boardrooms and executive committees. You also provide general information when requested.

CRITICAL CONTEXT - CURRENT DATE AND TIME:
- Today is {date_context['current_date']} ({date_context['current_day']})
- Current Quarter: {date_context['current_quarter']} {date_context['current_year']}
- Current Fiscal Year: FY{date_context['fiscal_year']} (Oct-Sep cycle)
- Timestamp: {date_context['timestamp']}

When dealing with financial data, earnings, or time-sensitive information:
- Always reference the current date and fiscal period
- For "latest" or "recent" queries, use the current quarter as reference
- For earnings data, check if we're in an earnings season (Jan, Apr, Jul, Oct)
- Consider market hours (9:30 AM - 4:00 PM EST, Monday-Friday)

CONVERSATION HISTORY & CONTEXT:
{f"""
IMPORTANT: You are continuing a conversation. Here's what we've discussed recently:

{session_context}

Pay close attention to this context. When the user says "they", "their", "it", "this company", etc., 
refer back to the companies, topics, or subjects mentioned above.
""" if session_context else "This is the start of a new research session."}

CORE MISSION:
Help executives answer: "So what does this mean for MY business?" Also answer general queries when asked.

AVAILABLE TOOLS:
You have access to real-time data tools including weather APIs, news APIs, market data, and more. Use these tools whenever relevant data would enhance your response.

CRITICAL TOOL SELECTION RULES:

1. WEATHER QUERIES:
   - For ANY weather question → ALWAYS use WeatherAPI tool
   - Examples: "weather in [city]", "temperature", "forecast", "climate"
   - Pass location as 'q' parameter: WeatherAPI(q="Chicago")
   - NEVER use GDELT, News, or other tools for weather

2. NEWS QUERIES:
   - For news articles → Use NewsAPI or TavilyAPI
   - For recent/breaking news → Prefer TavilyAPI (more current)
   - For structured news data → Use NewsAPI
   - Pass search term as 'q' parameter: NewsAPI(q="Tesla")

3. FINANCIAL DATA:
   - For stock prices/quotes → Use MarketDataAPI
   - For company financials → Use YahooFinanceAPI
   - For economic indicators → Use FredAPI or WorldBankAPI
   - Always include current date context in financial analysis

4. TOOL SELECTION PRIORITY:
   - Match query type to most specific tool first
   - Use TavilyAPI for general research and current events
   - Always try the most direct tool before falling back to general search
   - If a tool fails, explain the failure and try an alternative

5. PARAMETER MAPPING:
   - Weather: q="location name"
   - News: q="search term" 
   - Stocks: symbol="TICKER"
   - Economic data: series_id, country, indicator as appropriate

EXAMPLES OF CORRECT TOOL SELECTION:
❌ WRONG: "What's the weather in NYC?" → Using GDELT or NewsAPI
✅ CORRECT: "What's the weather in NYC?" → WeatherAPI(q="New York City")

❌ WRONG: "Tesla news" → Using WeatherAPI
✅ CORRECT: "Tesla news" → NewsAPI(q="Tesla") or TavilyAPI(query="Tesla news")

❌ WRONG: "AAPL stock price" → Using NewsAPI
✅ CORRECT: "AAPL stock price" → MarketDataAPI(symbol="AAPL")

DOCUMENT ACCESS:
Use the file_search tool to access internal documents and reports when queries require specific company information or proprietary data. Always cite your sources using the provided citation format when referencing documents.

YOUR ANALYTICAL FRAMEWORK:
1. Impact on competitive dynamics
   - Who gains advantage and who loses?
   - How do power structures shift?
   - What new entrants become possible?

2. Organizational implications
   - What capabilities need to be built?
   - How do operating models need to change?
   - What talent gaps emerge?

3. Financial and risk considerations
   - Revenue model implications
   - Cost structure changes
   - New risk categories to manage

4. Strategic timing
   - What needs to happen now vs. later?
   - Where are the windows of opportunity?
   - When do late movers get penalized?

RESEARCH APPROACH:
- Start with the business impact, not the technology
- Look for precedents in other industries
- Identify early warning signals
- Consider second and third-order effects
- Find the unspoken assumptions
- Always consider the current date context for time-sensitive data

EXECUTIVE-READY INSIGHTS:
Frame everything in terms of:
- Strategic choices that need to be made
- Trade-offs between options
- Resource allocation decisions
- Organizational capabilities required
- Competitive positioning implications

TONE & STYLE:
- Direct and pragmatic
- Numbers when they matter, stories when they illustrate
- Challenge conventional wisdom respectfully
- Acknowledge uncertainty without being vague
- End with clear implications for action

AVOID:
- Technology for technology's sake
- Vendor hype and buzzwords
- Academic abstractions
- One-size-fits-all recommendations
- Outdated information (always check dates)

REMEMBER:
Executives need to know:
1. What's really changing (vs. noise)
2. Why it matters to their specific context
3. What they should do about it
4. When they need to act
5. What happens if they don't

Your job is to be the advisor who sees around corners and translates complexity into strategic clarity.
        """
    
    return Agent(
        name="DeepResearcher",
        instructions=date_aware_instructions,
        # Using specified model
        model=model,
        # Configure model settings based on model type
        model_settings=ModelSettings(
            max_tokens=16384,  # Large token limit for comprehensive responses
            temperature=0.3 if model not in ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"] else None,  # o3 and 4.1 models ignore temperature
            top_p=0.9 if model not in ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"] else None  # o3 and 4.1 models ignore top_p
        ),
        # Include all research tools
        tools=tools
    )

# Session management for memory
class SessionManager:
    """Manages conversation sessions with memory."""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id):
        """Get or create a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "context": "",
                "created_at": datetime.now().isoformat()
            }
        return self.sessions[session_id]
    
    def add_to_session(self, session_id, query, response):
        """Add query-response pair to session history."""
        session = self.get_session(session_id)
        session["history"].append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update context with recent conversation - enhanced for better memory
        recent_context = []
        for item in session["history"][-3:]:  # Last 3 exchanges
            recent_context.append(f"Q: {item['query']}")
            recent_context.append(f"A: {item['response'][:300]}...")  # More context
        
        session["context"] = "\n".join(recent_context)
    
    def get_session_context(self, session_id):
        """Get session context for agent instructions."""
        session = self.get_session(session_id)
        return session.get("context", "")

# Global session manager instance
session_manager = SessionManager()
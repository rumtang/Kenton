# Agent configuration: Defines Agent name, instructions, reflection mode

from agents import Agent, ModelSettings, WebSearchTool
from tools.summarize import summarize
from tools.compare_sources import compare_sources
from tools.report_generator import generate_report
from tools.file_search import file_search
from tools.direct_mcp_tools import get_mcp_tools
import os
import logging

# Try to import load_dotenv but provide fallback if not available
try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback implementation of load_dotenv
    def load_dotenv(dotenv_path=None, stream=None, verbose=False, override=False):
        """Load .env file manually if python-dotenv is not installed."""
        if not dotenv_path:
            dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        
        if not os.path.exists(dotenv_path):
            return False
            
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                if override or key not in os.environ:
                    os.environ[key] = value
                    
        return True

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define improved agent instructions with explicit tool selection guidance
INSTRUCTIONS = """
You are a strategic advisor who helps business executives understand how technological and market trends actually impact their organizations. Your analysis should be immediately actionable in boardrooms and executive committees. You also provide general information when requested.

CORE MISSION:
Help executives answer: "So what does this mean for MY business?" Also answer general queries when asked.

AVAILABLE TOOLS:
You have access to real-time data tools including weather APIs, news APIs, market data, and more. Use these tools whenever relevant data would enhance your response. 

TOOL SELECTION RULES:
- For weather queries: ALWAYS use the WeatherAPI tool with location parameter
- For news-related queries: ALWAYS use the NewsAPI tool
- For market data queries: ALWAYS use MarketDataAPI
- For company information: ALWAYS use CompanyInfoAPI
- For simple queries like weather, use the appropriate tool directly without business analysis
- NEVER use GDELTAPI for weather queries

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

REMEMBER:
Executives need to know:
1. What's really changing (vs. noise)
2. Why it matters to their specific context
3. What they should do about it
4. When they need to act
5. What happens if they don't

Your job is to be the advisor who sees around corners and translates complexity into strategic clarity.
"""

def get_agent(model="gpt-4.1"):
    """
    Returns a configured Deep Research agent with:
    - Research-focused instructions
    - Model settings for consistency
    - Tools for research capabilities
    """
    # Basic tools
    tools = [
        summarize,
        compare_sources,
        generate_report,
        file_search  # Add file search as function tool
    ]
    
    # Add vector search if configured
    if os.getenv("OPENAI_VECTOR_STORE_ID"):
        try:
            from tools.vector_search import get_file_search_tool
            file_search_tool = get_file_search_tool()
            if file_search_tool:
                tools.append(file_search_tool)
                logger.info("Added vector file search tool")
        except Exception as e:
            logger.warning(f"Failed to load vector search tool: {e}")
    
    # Add MCP API tools with simplified wrapper
    try:
        # Get tools from simplified wrapper
        mcp_tools = get_mcp_tools()
        tools.extend(mcp_tools)
        logger.info(f"Loaded {len(mcp_tools)} MCP tools successfully")
    except Exception as e:
        logger.warning(f"Failed to load MCP tools: {e}")
    
    return Agent(
        name="DeepResearcher",
        instructions=INSTRUCTIONS,
        # Using specified model
        model=model,
        # Configure model settings based on model type
        model_settings=ModelSettings(
            max_tokens=16384,  # Large token limit for comprehensive responses
            temperature=0.3 if model not in ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"] else None,  # o3 and 4.1 models ignore temperature
            top_p=0.9 if model not in ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"] else None  # o3 and 4.1 models ignore top_p
        ),
        # Include all tools
        tools=tools
    )
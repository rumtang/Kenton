# Agent configuration: Defines Agent name, instructions, reflection mode

from agents import Agent, ModelSettings, WebSearchTool
from tools.summarize import summarize
from tools.compare_sources import compare_sources
from tools.report_generator import generate_report
from tools.file_search import file_search
import os
import logging
from task_complexity import determine_reasoning_effort

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
You have access to tools to help with research, analysis, and summarization. Use these tools whenever relevant data would enhance your response.

TOOL SELECTION RULES:
- For weather queries: Use the weather_api tool with a location parameter
- For document search: Use the file_search tool
- For comparing information: Use the compare_sources tool
- For generating reports: Use the generate_report tool
- For summarizing long content: Use the summarize tool

FINANCIAL DATA TOOLS:
You have access to Financial Modeling Prep APIs for comprehensive financial data:
- Use company_profile for basic company information 
- Use income_statement, balance_sheet, and cash_flow for financial statement analysis
- Use key_metrics and financial_ratios for performance evaluation
- Use stock_price for current quotes and historical_price for price history
- Use stock_news and market_news for market and company news

When analyzing companies:
1. Start with profile data to understand the business
2. Examine financial statements for detailed analysis
3. Use ratios and metrics for comparative evaluation
4. Check stock price performance for market perspective
5. Review recent news for qualitative context

Always include the required 'symbol' parameter for company-specific data.

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
    
    # Import financial API tools
    try:
        from tools.financial_api import (
            company_profile, income_statement, balance_sheet, cash_flow, 
            key_metrics, financial_ratios, stock_price, historical_price,
            stock_news, market_news
        )
        financial_tools = [
            company_profile, income_statement, balance_sheet, cash_flow, 
            key_metrics, financial_ratios, stock_price, historical_price,
            stock_news, market_news
        ]
        api_tools.extend(financial_tools)
        logger.info(f"Added {len(financial_tools)} financial API tools")
    except ImportError:
        logger.warning("Financial API tools not available")
    
    logger.info(f"Loaded {len(api_tools)} API tools total")
    return api_tools

def get_agent(model="gpt-4.1", enable_reasoning=False, query=""):
    """
    Returns a configured Deep Research agent with:
    - Research-focused instructions
    - Model settings for consistency
    - Tools for research capabilities
    - Optional reasoning capabilities (for compatible models)
    
    Args:
        model (str): The model to use (e.g. "gpt-4.1", "o3", "o3-mini")
        enable_reasoning (bool): Whether to enable reasoning features
        query (str): The query to analyze for determining reasoning effort
    """
    # Determine which tools are compatible with this model
    reasoning_models = ["o3", "o4-mini", "o3-mini", "o3o"]
    is_reasoning_model = model in reasoning_models
    
    # For reasoning models, we need to be careful about which tools we include
    # as some hosted tools are not supported with o3
    if is_reasoning_model:
        # Basic tools that are compatible with reasoning models
        tools = [
            summarize,
            compare_sources,
            generate_report
            # No file_search for reasoning models, per API error
        ]
    else:
        # Basic tools for non-reasoning models
        tools = [
            summarize,
            compare_sources,
            generate_report,
            file_search  # Include file search for non-reasoning models
        ]
        
        # Add vector search if configured (only for non-reasoning models)
        if os.getenv("OPENAI_VECTOR_STORE_ID"):
            try:
                from tools.vector_search import get_file_search_tool
                file_search_tool = get_file_search_tool()
                if file_search_tool:
                    tools.append(file_search_tool)
                    logger.info("Added vector file search tool")
            except Exception as e:
                logger.warning(f"Failed to load vector search tool: {e}")

    # Add API tools
    try:
        api_tools = get_api_tools()
        if api_tools:
            tools.extend(api_tools)
            logger.info(f"Loaded {len(api_tools)} API tools successfully")
    except Exception as e:
        logger.warning(f"Failed to load API tools: {e}")
    
    # Determine if reasoning is supported by this model
    reasoning_compatible_models = ["o3", "o4-mini", "o3-mini", "o3o", "gpt-4.1", "gpt-4.1-mini"]
    can_use_reasoning = model in reasoning_compatible_models and enable_reasoning
    
    if can_use_reasoning:
        logger.info(f"Enabling reasoning capabilities for model: {model}")
    
    # Set up model settings based on model type and reasoning preference
    if model in reasoning_compatible_models:
        # For reasoning-compatible models, we don't need to specify temperature and top_p
        # as they'll be automatically optimized for reasoning capability
        
        # Use standard model settings but adjust for reasoning if needed
        model_settings = ModelSettings(
            max_tokens=16384,  # Large token limit for comprehensive responses
        )
        
        # Set reasoning parameter when enabled (based on API documentation)
        if enable_reasoning:
            # For o3, reasoning effort parameter needs to be set as an object with effort property
            # We'll use adaptive reasoning based on the task complexity
            if query:
                # Determine effort level based on query
                effort = determine_reasoning_effort(query)
                logger.info(f"Setting reasoning effort to '{effort}' based on query complexity")
            else:
                # Default to medium if no query is provided
                effort = "medium"
                logger.info(f"Setting reasoning effort to default '{effort}'")
                
            model_settings.reasoning = {"effort": effort}
    else:
        # For other models, use our standard settings
        model_settings = ModelSettings(
            max_tokens=16384,  # Large token limit for comprehensive responses
            temperature=0.3,  # Claude works well with this temperature
            top_p=0.9  # Keep reasonable top_p for quality
        )
    
    return Agent(
        name="DeepResearcher",
        instructions=INSTRUCTIONS,
        model=model,
        model_settings=model_settings,
        tools=tools
    )
# Agent configuration: Defines Agent name, instructions, reflection mode

from agents import Agent, ModelSettings, WebSearchTool
from tools.summarize import summarize
from tools.compare_sources import compare_sources
from tools.report_generator import generate_report
from tools.file_search import file_search
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
You have access to tools to help with research, analysis, and summarization. Use these tools whenever relevant data would enhance your response.

TOOL SELECTION RULES:
- For weather queries: Use the weather_api tool with a location parameter
- For document search: Use the file_search tool
- For comparing information: Use the compare_sources tool
- For generating reports: Use the generate_report tool
- For summarizing long content: Use the summarize tool

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
    
    logger.info(f"Loaded {len(api_tools)} API tools")
    return api_tools

def get_agent(model="gpt-4.1"):
    """
    Returns a configured Deep Research agent with:
    - Research-focused instructions
    - Model settings for consistency
    - Tools for research capabilities
    """
    # Basic tools that work with all models
    tools = [
        summarize,
        compare_sources,
        generate_report,
        file_search  # Always include file search
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

    # Add API tools
    try:
        api_tools = get_api_tools()
        if api_tools:
            tools.extend(api_tools)
            logger.info(f"Loaded {len(api_tools)} API tools successfully")
    except Exception as e:
        logger.warning(f"Failed to load API tools: {e}")
    
    return Agent(
        name="DeepResearcher",
        instructions=INSTRUCTIONS,
        model=model,
        model_settings=ModelSettings(
            max_tokens=16384,  # Large token limit for comprehensive responses
            temperature=0.3,  # Claude works well with this temperature
            top_p=0.9  # Keep reasonable top_p for quality
        ),
        tools=tools
    )
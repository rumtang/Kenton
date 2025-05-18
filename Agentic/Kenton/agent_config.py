# Agent configuration: Defines Agent name, instructions, reflection mode

from agents import Agent, ModelSettings, WebSearchTool
from tools.summarize import summarize
from tools.compare_sources import compare_sources
from tools.report_generator import generate_report
from tools.file_search import file_search
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_agent(model="o3-responses"):
    """
    Returns a configured Deep Research agent with:
    - Research-focused instructions
    - Model settings for consistency
    - Tools for research capabilities
    """
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
    
    return Agent(
        name="DeepResearcher",
        instructions="""
You are a strategic advisor who helps business executives understand how technological and market trends actually impact their organizations. Your analysis should be immediately actionable in boardrooms and executive committees.

CORE MISSION:
Help executives answer: "So what does this mean for MY business?"

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
        """,
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
#!/usr/bin/env python3
"""
Module for determining the appropriate reasoning effort based on task complexity.
Uses a simple heuristic to assess query complexity and set reasoning effort level.
"""

import re
from typing import Literal

# Type for reasoning effort levels
ReasoningEffort = Literal["low", "medium", "high"]

# Complexity indicators
COMPLEX_TERMS = [
    "explain in detail", "analyze", "compare and contrast",
    "evaluate", "synthesize", "design", "develop a framework",
    "in depth", "comprehensive", "systematic", "methodology",
    "complex", "complicated", "technical", "advanced",
    "pros and cons", "advantages and disadvantages",
    "critically", "thoroughly", "exhaustively", "precisely"
]

MATH_TERMS = [
    "calculate", "compute", "solve", "equation", "formula",
    "mathematical", "algorithm", "statistics", "probability",
    "derivative", "integral", "calculus", "algebra", "geometry"
]

SIMPLE_TERMS = [
    "briefly", "summarize", "list", "short", "quick",
    "simple", "basic", "beginner", "introduction", "overview",
    "gist", "outline", "summary", "concise", "briefly explain"
]

def count_complexity_indicators(query: str) -> dict:
    """Count the number of complexity indicators in the query."""
    query = query.lower()
    
    # Count occurrences of each type of indicator
    complex_count = sum(1 for term in COMPLEX_TERMS if term in query)
    math_count = sum(1 for term in MATH_TERMS if term in query)
    simple_count = sum(1 for term in SIMPLE_TERMS if term in query)
    
    # Count words as basic complexity measure
    word_count = len(re.findall(r'\w+', query))
    
    return {
        "complex_count": complex_count,
        "math_count": math_count,
        "simple_count": simple_count,
        "word_count": word_count
    }

def determine_reasoning_effort(query: str) -> ReasoningEffort:
    """
    Determine the appropriate reasoning effort based on query complexity.
    
    Args:
        query: The user's query
        
    Returns:
        The appropriate reasoning effort level as "low", "medium", or "high"
    """
    indicators = count_complexity_indicators(query)
    
    # Default to medium
    effort = "medium"
    
    # Override based on indicators
    if indicators["simple_count"] > 0 and indicators["word_count"] < 20:
        # Simple, short queries
        effort = "low"
    elif indicators["math_count"] > 0 or indicators["complex_count"] > 1:
        # Math or multiple complex indicators
        effort = "high"
    elif indicators["word_count"] > 30:
        # Longer queries that aren't explicitly simple
        effort = "high"
    
    return effort  # type: ignore
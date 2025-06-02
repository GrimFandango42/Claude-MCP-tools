"""
Code Intelligence Core Framework

Shared utilities for code intelligence MCP servers.
"""

from .core import (
    CodeIntelligenceCore,
    CodeAnalysis,
    Symbol,
    LanguageType,
    get_core
)

__version__ = "0.1.0"
__all__ = [
    "CodeIntelligenceCore",
    "CodeAnalysis", 
    "Symbol",
    "LanguageType",
    "get_core"
]
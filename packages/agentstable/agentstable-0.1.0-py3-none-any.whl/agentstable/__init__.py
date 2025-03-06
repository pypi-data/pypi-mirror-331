"""
AgentsTable SDK - A Python SDK for interacting with the AgentsTable ecosystem.
"""

from .client import (
    AgentsClient,
    search,
    get_tools,
    get_tools_json,
    execute,
    stream_execute,
    execute_flow,
    get_and_execute_flow,
    get_flow,
    stream_llm,
    parse_llm_response,
)

from .models import (
    AgentsJSON,
    Flow as FlowModel,
    Tool as ToolModel,
    Link,
    SearchResults,
    OpenAITool,
    OpenAIFunction,
    AnthropicTool,
    AnthropicTools,
    Authentication as AuthenticationModel,
)

from .providers import (
    WikipediaProvider,
    MemoryProvider,
)

from .utils.flow import (
    FlowExecutor,
    Flow,
    Tool,
)

from .utils.parser import AgentsJSONParser
from .utils.validator import AgentsJSONValidator

__all__ = [
    # Client
    "AgentsClient",
    
    # Function aliases
    "search",
    "get_tools",
    "get_tools_json",
    "execute",
    "stream_execute",
    "execute_flow",
    "get_and_execute_flow",
    "get_flow",
    "stream_llm",
    "parse_llm_response",
    
    # Models
    "AgentsJSON",
    "FlowModel",
    "ToolModel",
    "Link",
    "SearchResults",
    "OpenAITool",
    "OpenAIFunction",
    "AnthropicTool",
    "AnthropicTools",
    "AuthenticationModel",
    
    # Providers
    "WikipediaProvider",
    "MemoryProvider",
    
    # Flow execution
    "FlowExecutor",
    "Flow",
    "Tool",
    
    # Utilities
    "AgentsJSONParser",
    "AgentsJSONValidator",
]

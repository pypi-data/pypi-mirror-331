from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class Authentication(BaseModel):
    """Authentication information for the agent."""
    type: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class InputSchema(BaseModel):
    """Input schema for a tool."""
    type: str
    properties: Dict[str, Any]
    required: Optional[List[str]] = None

class Tool(BaseModel):
    """Tool definition in an agents.json file."""
    name: str
    description: str
    input_schema: InputSchema
    authentication: Optional[Authentication] = None
    service_provider: Optional[str] = None

class Link(BaseModel):
    """Link between tools in a flow."""
    source: str
    target: str
    source_field: str
    target_field: str
    description: Optional[str] = None

class Flow(BaseModel):
    """Flow definition in an agents.json file."""
    id: str
    name: str
    description: str
    tools: List[Tool]
    links: Optional[List[Link]] = None
    provider: Optional[str] = None

class AgentsJSON(BaseModel):
    """Root agents.json schema."""
    provider: str
    provider_id: str
    version: str = "0.1.0"
    flows: List[Flow]
    
class SearchResults(BaseModel):
    """Search results from the Tool Discovery Service."""
    flows: List[Flow]
    total: int
    query: str

class OpenAIParameter(BaseModel):
    """OpenAI parameter schema."""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None

class OpenAIParametersSchema(BaseModel):
    """OpenAI parameters schema."""
    type: str
    properties: Dict[str, OpenAIParameter]
    required: Optional[List[str]] = None

class OpenAIFunction(BaseModel):
    """OpenAI function schema."""
    name: str
    description: Optional[str] = None
    parameters: OpenAIParametersSchema

class OpenAITool(BaseModel):
    """OpenAI tool schema."""
    type: str = "function"
    function: OpenAIFunction

class AnthropicSchema(BaseModel):
    """Anthropic tool input schema."""
    type: str
    properties: Dict[str, Any]
    required: Optional[List[str]] = None

class AnthropicTool(BaseModel):
    """Anthropic tool schema."""
    name: str
    description: Optional[str] = None
    input_schema: AnthropicSchema

class AnthropicTools(BaseModel):
    """Anthropic tools container."""
    tools: List[AnthropicTool]

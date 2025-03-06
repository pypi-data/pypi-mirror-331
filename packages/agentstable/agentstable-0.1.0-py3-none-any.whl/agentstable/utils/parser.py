import json
import requests
from typing import Any, Dict, List, Optional, Union

from ..models import (
    AgentsJSON, 
    Flow, 
    Tool, 
    Link,
    OpenAITool,
    OpenAIFunction,
    OpenAIParametersSchema,
    AnthropicTool,
    AnthropicSchema,
    AnthropicTools
)

class AgentsJSONParser:
    """Parser for agents.json files."""
    
    def parse(self, data: Dict) -> AgentsJSON:
        """
        Parse a dict into an AgentsJSON object.
        
        Args:
            data: Dict containing agents.json data
            
        Returns:
            AgentsJSON object
        """
        return AgentsJSON(**data)
    
    def parse_file(self, file_path: str) -> AgentsJSON:
        """
        Parse an agents.json file.
        
        Args:
            file_path: Path to the agents.json file
            
        Returns:
            AgentsJSON object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.parse(data)
    
    def parse_url(self, url: str) -> AgentsJSON:
        """
        Parse an agents.json file from a URL.
        
        Args:
            url: URL to fetch the agents.json file from
            
        Returns:
            AgentsJSON object
        """
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        return self.parse(data)
    
    def to_openai_tools(self, flow: Flow) -> List[Dict]:
        """
        Convert flow tools to OpenAI tools format.
        
        Args:
            flow: Flow to convert
            
        Returns:
            List of tools in OpenAI format
        """
        openai_tools = []
        
        for tool in flow.tools:
            openai_tool = self._convert_tool_to_openai(tool)
            openai_tools.append(openai_tool.dict())
        
        return openai_tools
    
    def to_anthropic_tools(self, flow: Flow) -> List[Dict]:
        """
        Convert flow tools to Anthropic tools format.
        
        Args:
            flow: Flow to convert
            
        Returns:
            List of tools in Anthropic format
        """
        anthropic_tools = []
        
        for tool in flow.tools:
            anthropic_tool = self._convert_tool_to_anthropic(tool)
            anthropic_tools.append(anthropic_tool.dict())
        
        return anthropic_tools
    
    def _convert_tool_to_openai(self, tool: Tool) -> OpenAITool:
        """
        Convert a Tool to OpenAI format.
        
        Args:
            tool: Tool to convert
            
        Returns:
            OpenAITool
        """
        # Convert properties to OpenAI format
        properties = {}
        for prop_name, prop_schema in tool.input_schema.properties.items():
            properties[prop_name] = {
                "type": prop_schema.get("type", "string"),
                "description": prop_schema.get("description", "")
            }
            
            # Add enum if present
            if "enum" in prop_schema:
                properties[prop_name]["enum"] = prop_schema["enum"]
        
        # Create OpenAI function
        function = OpenAIFunction(
            name=tool.name.lower().replace(" ", "_"),
            description=tool.description,
            parameters=OpenAIParametersSchema(
                type="object",
                properties=properties,
                required=tool.input_schema.required if tool.input_schema.required else []
            )
        )
        
        # Create OpenAI tool
        return OpenAITool(function=function)
    
    def _convert_tool_to_anthropic(self, tool: Tool) -> AnthropicTool:
        """
        Convert a Tool to Anthropic format.
        
        Args:
            tool: Tool to convert
            
        Returns:
            AnthropicTool
        """
        # Create an AnthropicSchema from the InputSchema
        anthropic_schema = AnthropicSchema(
            type=tool.input_schema.type,
            properties=tool.input_schema.properties,
            required=tool.input_schema.required if tool.input_schema.required else []
        )
        
        return AnthropicTool(
            name=tool.name.lower().replace(" ", "_"),
            description=tool.description,
            input_schema=anthropic_schema
        )

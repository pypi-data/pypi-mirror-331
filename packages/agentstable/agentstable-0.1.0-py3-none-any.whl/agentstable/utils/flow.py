"""
Flow execution utilities for the agentstable SDK.

This module provides functionality for executing multi-tool flows
based on the agents.json specification pattern.
"""

import json
from typing import Dict, List, Any, Optional, Callable, Union
import logging

class Tool:
    """
    Represents a tool in a flow.
    
    A tool corresponds to an API endpoint or function.
    """
    
    def __init__(self, 
                 id: str = None, 
                 name: str = None, 
                 description: str = None,
                 parameters: Dict[str, Any] = None,
                 function: Optional[Union[str, Dict[str, Any]]] = None,
                 provider: str = None,
                 type: str = None,
                 **kwargs):
        """
        Initialize a Tool object.
        
        Args:
            id: Unique identifier for the tool
            name: Display name for the tool
            description: Description of what the tool does
            parameters: Parameter definition for the tool
            function: Function name to call or function definition
            provider: Provider ID for the tool
            type: Tool type (e.g., 'function')
            **kwargs: Additional tool properties
        """
        # Handle OpenAI format tools
        if type == "function" and isinstance(function, dict):
            self.id = id or function.get("name", "unknown")
            self.name = function.get("name", name or "Unknown Tool")
            self.description = function.get("description", description or "")
            self.parameters = function.get("parameters", parameters or {})
            self.function = function.get("name")
            self.provider = provider
            self.type = type
        else:
            self.id = id or name or "unknown"
            self.name = name or "Unknown Tool"
            self.description = description or ""
            self.parameters = parameters or {}
            self.function = function
            self.provider = provider
            self.type = type
        
        # Store any additional properties
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class Flow:
    """
    Represents a multi-tool flow from the Tool Discovery service.
    
    A flow is a collection of tools that can be executed together.
    """
    
    def __init__(self, 
                 id: str, 
                 name: str = None, 
                 provider: str = None,
                 description: str = "", 
                 tools: List[Union[Dict, Tool]] = None,
                 links: List[Dict] = None):
        """
        Initialize a Flow object.
        
        Args:
            id: Unique identifier for the flow
            name: Display name for the flow
            provider: Provider ID for the flow
            description: Optional description of the flow
            tools: List of tools in the flow (can be dictionaries or Tool objects)
            links: Optional list of links between tools
        """
        self.id = id
        self.name = name or id
        self.description = description
        self.provider = provider or id.split(":")[0] if ":" in id else "unknown"
        
        # Convert tool dictionaries to Tool objects if necessary
        self.tools = []
        if tools:
            for tool in tools:
                if isinstance(tool, Dict):
                    self.tools.append(Tool(**tool))
                else:
                    self.tools.append(tool)
        
        self.links = links or []
        
    def get_tool_by_id(self, tool_id: str) -> Optional[Tool]:
        """
        Get a tool by its ID.
        
        Args:
            tool_id: ID of the tool to find
            
        Returns:
            Tool object if found, None otherwise
        """
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        return None


class FlowExecutor:
    """
    Executes a multi-tool flow from the Tool Discovery service.
    
    Handles executing tools in sequence, managing data flow between tools.
    """
    
    def __init__(self, execute_tool_fn: Callable[[str, Dict[str, Any], Optional[Dict]], Any]):
        """
        Initialize a FlowExecutor.
        
        Args:
            execute_tool_fn: Function to execute a single tool with parameters
        """
        self.execute_tool = execute_tool_fn
        self.results_cache = {}
    
    def execute_flow(self, flow: Flow, parameters: Dict[str, Any], auth: Optional[Dict] = None, tool_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a multi-tool flow.
        
        Executes tools in sequence, passing data between them based on links.
        
        Args:
            flow: Flow definition
            parameters: Parameters for the flow execution
            auth: Optional authentication details
            tool_sequence: Optional sequence of tool IDs to execute (defaults to all tools in order)
            
        Returns:
            Dict containing the results of all executed tools
        """
        # Clear previous results
        self.results_cache = {}
        
        # Default to all tools if no sequence provided
        if not tool_sequence:
            tool_sequence = [tool.id for tool in flow.tools]
        
        # Execute each tool in sequence
        for tool_id in tool_sequence:
            tool = flow.get_tool_by_id(tool_id)
            if not tool:
                logging.warning(f"Tool '{tool_id}' not found in flow '{flow.id}'")
                continue
            
            # Prepare parameters for this tool
            tool_parameters = self._prepare_parameters(tool, parameters, flow.links)
            
            # Execute the tool
            result = self.execute_tool(tool.id, tool_parameters, auth)
            
            # Store the result
            self.results_cache[tool_id] = result
        
        return self.results_cache
    
    def _prepare_parameters(self, tool: Tool, global_parameters: Dict[str, Any], links: List[Dict]) -> Dict[str, Any]:
        """
        Prepare parameters for tool execution.
        
        Combines global parameters with values from previous tool results based on links.
        
        Args:
            tool: Tool to prepare parameters for
            global_parameters: Global parameters for the flow
            links: Links between tools
            
        Returns:
            Dict of parameters for the tool
        """
        # Start with global parameters
        tool_parameters = global_parameters.copy()
        
        # Apply links from previous tool results
        for link in links:
            if link.get("target") == tool.id:
                source_tool_id = link.get("source")
                source_parameter = link.get("source_parameter")
                target_parameter = link.get("target_parameter")
                
                if source_tool_id in self.results_cache and source_parameter and target_parameter:
                    # Get the value from the source tool's result
                    source_result = self.results_cache[source_tool_id]
                    
                    # Handle dot notation for nested properties
                    value = self._resolve_parameter_value(source_result, source_parameter)
                    
                    # Set the value in the target parameters
                    tool_parameters[target_parameter] = value
        
        return tool_parameters
    
    def _resolve_parameter_value(self, data: Any, parameter: str) -> Any:
        """
        Resolve a parameter value from data.
        
        Handles dot notation for nested properties.
        
        Args:
            data: Data to extract value from
            parameter: Parameter path (e.g. "result.items[0].name")
            
        Returns:
            Extracted value
        """
        # Handle simple case
        if parameter in data:
            return data[parameter]
        
        # Handle dot notation
        if "." in parameter:
            parts = parameter.split(".", 1)
            key, rest = parts[0], parts[1]
            
            # Handle array indexing
            if "[" in key and key.endswith("]"):
                array_key, index_str = key.split("[", 1)
                index = int(index_str[:-1])
                
                if array_key in data and isinstance(data[array_key], list) and len(data[array_key]) > index:
                    return self._resolve_parameter_value(data[array_key][index], rest)
            elif key in data and isinstance(data[key], (dict, list)):
                return self._resolve_parameter_value(data[key], rest)
        
        # Return None if not found
        return None
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the results of all executed tools.
        
        Returns:
            Dict mapping tool IDs to their results
        """
        return self.results_cache 
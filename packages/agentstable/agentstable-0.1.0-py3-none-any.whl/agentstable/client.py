import json
import os
import requests
from typing import Any, Dict, List, Optional, Union, Generator, Callable

from .models import (
    AgentsJSON, 
    Flow, 
    SearchResults, 
    OpenAITool, 
    AnthropicTools,
    Tool
)
from .utils.parser import AgentsJSONParser
from .utils.validator import AgentsJSONValidator
from .utils.flow import FlowExecutor

# Default service URL
DEFAULT_SERVICE_URL = "https://tool-discovery-service-qcsgp633aq-uc.a.run.app"

class AgentsClient:
    """Client for interacting with agents.json files and the Tool Discovery Service."""
    
    def __init__(self, service_url: str = DEFAULT_SERVICE_URL):
        """
        Initialize the AgentsClient.
        
        Args:
            service_url: URL of the Tool Discovery service
        """
        self.service_url = service_url
        self.validators = {
            "agents_json": AgentsJSONValidator()
        }
        self.flow_executor = FlowExecutor(self.execute_tool)
        self.parser = AgentsJSONParser()
        self.agents_json_cache = {}
    
    def search(self, query: str, limit: int = 5, collection_id: Optional[str] = None) -> SearchResults:
        """
        Search for tools based on a natural language query.
        
        Args:
            query: Natural language query
            limit: Maximum number of results to return
            collection_id: Optional collection ID to limit search to
            
        Returns:
            SearchResults containing matching flows
        """
        url = f"{self.service_url}/search/"
        
        payload = {
            "query": query,
            "limit": limit
        }
        
        if collection_id:
            payload["collection_id"] = collection_id
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return SearchResults(**result)
    
    def get_tools(self, flow_id: str, format: str = "openai") -> Union[List[Dict], Dict]:
        """
        Get tools for a specific flow in a format suitable for language models.
        
        Args:
            flow_id: ID of the flow in format "provider_id:flow_id"
            format: Format of the tools (openai or anthropic)
            
        Returns:
            Tools in the requested format
        """
        url = f"{self.service_url}/tools/{flow_id}"
        
        params = {
            "format": format
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_tools_json(self, flow_id: str) -> Dict[str, Any]:
        """
        Get raw tools JSON for a specific flow.
        
        Args:
            flow_id: ID of the flow in format "provider_id:flow_id"
            
        Returns:
            Raw tools JSON
        """
        url = f"{self.service_url}/tools/{flow_id}"
        
        response = requests.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def load_agents_json(self, file_path: str, provider_id: str) -> AgentsJSON:
        """
        Load and parse an agents.json file.
        
        Args:
            file_path: Path to the agents.json file
            provider_id: ID for the provider
            
        Returns:
            Parsed AgentsJSON object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate the agents.json file
        self.validators["agents_json"].validate(data)
        
        # Set the provider ID if not present
        if "provider_id" not in data:
            data["provider_id"] = provider_id
        
        agents_json = AgentsJSON(**data)
        self.agents_json_cache[provider_id] = agents_json
        
        return agents_json
    
    def load_agents_json_from_url(self, url: str, provider_id: str) -> AgentsJSON:
        """
        Load and parse an agents.json file from a URL.
        
        Args:
            url: URL to fetch the agents.json file from
            provider_id: ID for the provider
            
        Returns:
            Parsed AgentsJSON object
        """
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Validate the agents.json file
        self.validators["agents_json"].validate(data)
        
        # Set the provider ID if not present
        if "provider_id" not in data:
            data["provider_id"] = provider_id
        
        agents_json = AgentsJSON(**data)
        self.agents_json_cache[provider_id] = agents_json
        
        return agents_json
    
    def upload_agents_json(self, file_path: str, provider_id: str, collection_id: Optional[str] = None) -> Dict:
        """
        Upload an agents.json file to the Tool Discovery Service.
        
        Args:
            file_path: Path to the agents.json file
            provider_id: ID for the provider
            collection_id: Optional collection ID to add the flows to
            
        Returns:
            Dict containing upload results
        """
        url = f"{self.service_url}/upload/"
        
        files = {
            'file': open(file_path, 'rb')
        }
        
        data = {
            'provider_id': provider_id
        }
        
        if collection_id:
            data['collection_id'] = collection_id
        
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def upload_agents_json_from_url(self, url: str, provider_id: str, collection_id: Optional[str] = None) -> Dict:
        """
        Upload an agents.json file from a URL to the Tool Discovery Service.
        
        Args:
            url: URL to fetch the agents.json file from
            provider_id: ID for the provider
            collection_id: Optional collection ID to add the flows to
            
        Returns:
            Dict containing upload results
        """
        api_url = f"{self.service_url}/upload/url"
        
        payload = {
            'provider_id': provider_id,
            'url': url
        }
        
        if collection_id:
            payload['collection_id'] = collection_id
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def execute_flow(self, flow_id: str, parameters: Dict, auth: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Execute a flow with the provided parameters.
        
        Args:
            flow_id: ID of the flow to execute
            parameters: Parameters for the flow
            auth: Optional authentication
            
        Returns:
            Dict containing execution results
        """
        return self.get_and_execute_flow(flow_id, parameters, auth)
    
    def stream_execute_flow(self, flow_id: str, parameters: Dict, auth: Optional[Dict[str, Any]] = None, chunk_size: int = 1024) -> Generator[Dict[str, Any], None, None]:
        """
        Stream execution of a flow with the provided parameters.
        
        Args:
            flow_id: ID of the flow to execute
            parameters: Parameters for the flow
            auth: Optional authentication
            chunk_size: Size of chunks to stream (default: 1024)
            
        Returns:
            Generator yielding chunks of the execution result
        """
        # Implementation...
        yield {"error": "Not implemented"}
    
    def stream_llm_response(self, model: str, messages: List[Dict[str, Any]], provider: str = "anthropic", max_tokens: int = 1000, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a response from an LLM using the provided messages.
        
        Args:
            model: The model to use (e.g., "claude-3-opus-20240229")
            messages: List of message dictionaries
            provider: The LLM provider ("anthropic" or "openai")
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the LLM
            
        Yields:
            Dict chunks of LLM response
        """
        # Check if the required library is available
        if provider.lower() == "anthropic":
            try:
                import anthropic
            except ImportError:
                yield {"error": "Anthropic Python SDK not installed. Install with: pip install anthropic"}
                return
            
            # Get API key from environment or kwargs
            api_key = kwargs.pop("api_key", os.environ.get("ANTHROPIC_API_KEY"))
            if not api_key:
                yield {"error": "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or pass as api_key parameter."}
                return
            
            # Initialize client and stream
            client = anthropic.Anthropic(api_key=api_key)
            try:
                with client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    messages=messages,
                    **kwargs
                ) as stream:
                    yield {"type": "start", "provider": "anthropic", "model": model}
                    
                    for text in stream.text_stream:
                        yield {"type": "content", "content": text}
                    
                    # Get the full message when complete
                    yield {"type": "complete", "message": stream.get_final_message().model_dump()}
            
            except Exception as e:
                yield {"type": "error", "error": str(e)}
        
        elif provider.lower() == "openai":
            try:
                import openai
            except ImportError:
                yield {"error": "OpenAI Python SDK not installed. Install with: pip install openai"}
                return
            
            # Get API key from environment or kwargs
            api_key = kwargs.pop("api_key", os.environ.get("OPENAI_API_KEY"))
            if not api_key:
                yield {"error": "OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass as api_key parameter."}
                return
            
            # Initialize client and stream
            client = openai.OpenAI(api_key=api_key)
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    **kwargs
                )
                
                yield {"type": "start", "provider": "openai", "model": model}
                
                collected_message = {"role": "assistant", "content": ""}
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        collected_message["content"] += content
                        yield {"type": "content", "content": content}
                
                # Complete message when done
                yield {"type": "complete", "message": collected_message}
            
            except Exception as e:
                yield {"type": "error", "error": str(e)}
        
        else:
            yield {"error": f"Unsupported provider: {provider}. Supported providers are 'anthropic' and 'openai'."}

    def execute_tool(self, tool_id: str, parameters: Dict[str, Any], auth: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool with parameters.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Parameters for the tool
            auth: Optional authentication information (api_key, bearer_token, or basic_auth)
            
        Returns:
            Tool execution result
        """
        url = f"{self.service_url}/execute/{tool_id}"
        
        headers = {}
        
        # Add authentication if provided
        if auth:
            if "api_key" in auth:
                headers["X-API-Key"] = auth["api_key"]
            elif "bearer_token" in auth:
                headers["Authorization"] = f"Bearer {auth['bearer_token']}"
            elif "basic_auth" in auth and "username" in auth["basic_auth"] and "password" in auth["basic_auth"]:
                import base64
                auth_str = f"{auth['basic_auth']['username']}:{auth['basic_auth']['password']}"
                encoded = base64.b64encode(auth_str.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        
        response = requests.post(url, json=parameters, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def execute_flow_from_definition(self, flow: Flow, parameters: Dict[str, Any], auth: Optional[Dict[str, Any]] = None, tool_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute a multi-tool flow using a flow definition.
        
        Args:
            flow: Flow definition
            parameters: Parameters for the flow
            auth: Optional authentication information
            tool_sequence: Optional sequence of tool IDs to execute
            
        Returns:
            Dict with results from all tools in the flow
        """
        return self.flow_executor.execute_flow(flow, parameters, auth, tool_sequence)

    def get_and_execute_flow(self, flow_id: str, parameters: Dict[str, Any], auth: Optional[Dict[str, Any]] = None, tool_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
        """Retrieve and execute a multi-tool flow."""
        flow = self.get_flow(flow_id)
        return self.execute_flow_from_definition(flow, parameters, auth, tool_sequence)
    
    def get_flow(self, flow_id: str) -> Flow:
        """
        Get a flow definition by ID.
        
        Args:
            flow_id: ID of the flow in format "provider_id:flow_id"
            
        Returns:
            Flow definition
        """
        tools_json = self.get_tools_json(flow_id)
        
        # Handle different response formats (list or dictionary)
        if isinstance(tools_json, list):
            # If it's a list of tools, create a flow with these tools
            provider_id = flow_id.split(":")[0] if ":" in flow_id else "unknown"
            flow_name = flow_id.split(":")[-1] if ":" in flow_id else flow_id
            
            flow_def = {
                "id": flow_id,
                "name": flow_name,
                "provider": provider_id,
                "tools": tools_json,
                "description": f"Flow for {flow_name}"
            }
        else:
            # If it's already a flow definition
            flow_def = tools_json
        
        # Use our custom Flow class instead of Pydantic model
        from .utils.flow import Flow
        return Flow(**flow_def)

# Function aliases for simplified use
def search(query: str, limit: int = 5, collection_id: Optional[str] = None) -> SearchResults:
    """Search for tools based on a natural language query."""
    client = AgentsClient()
    return client.search(query, limit, collection_id)

def get_tools(flow_id: str, format: str = "openai") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Get tools for a specific flow in a format suitable for language models."""
    client = AgentsClient()
    return client.get_tools(flow_id, format)

def get_tools_json(flow_id: str) -> Dict[str, Any]:
    """Get raw tools JSON for a specific flow."""
    client = AgentsClient()
    return client.get_tools_json(flow_id)

def execute(flow_id: str, parameters: Dict, auth: Optional[Dict[str, Any]] = None) -> Dict:
    """Execute a flow with the provided parameters."""
    client = AgentsClient()
    return client.execute_flow(flow_id, parameters, auth)

def stream_execute(flow_id: str, parameters: Dict, auth: Optional[Dict[str, Any]] = None, chunk_size: int = 1024) -> Generator[Dict[str, Any], None, None]:
    """Stream execution of a flow with the provided parameters."""
    client = AgentsClient()
    return client.stream_execute_flow(flow_id, parameters, auth, chunk_size)

def execute_flow(flow: Flow, parameters: Dict, auth: Optional[Dict[str, Any]] = None, tool_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
    """Execute a multi-tool flow with the provided parameters."""
    client = AgentsClient()
    return client.execute_flow_from_definition(flow, parameters, auth, tool_sequence)

def get_and_execute_flow(flow_id: str, parameters: Dict, auth: Optional[Dict[str, Any]] = None, tool_sequence: Optional[List[str]] = None) -> Dict[str, Any]:
    """Retrieve and execute a multi-tool flow."""
    client = AgentsClient()
    return client.get_and_execute_flow(flow_id, parameters, auth, tool_sequence)

def get_flow(flow_id: str) -> Flow:
    """Get a flow definition by ID."""
    client = AgentsClient()
    return client.get_flow(flow_id)

def stream_llm(model: str, 
              messages: List[Dict[str, Any]], 
              tools: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None, 
              provider: str = "anthropic") -> Generator[Dict[str, Any], None, None]:
    """
    Stream responses from an LLM with tools.
    
    Args:
        model: The model to use
        messages: The conversation messages
        tools: The tools to provide to the model
        provider: The provider to use (anthropic or openai)
        
    Yields:
        Chunks of the response
    """
    client = AgentsClient()
    yield from client.stream_llm(model, messages, tools, provider)

def parse_llm_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a response from an LLM to extract tool calls.
    
    Args:
        response: The response from the LLM
        
    Returns:
        Parsed response with tool calls
    """
    client = AgentsClient()
    return client.parse_llm_response(response)

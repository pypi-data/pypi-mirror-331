#!/usr/bin/env python3
"""
Test script for the multi-tool flow execution functionality in the AgentsTable SDK.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from agentstable.utils.flow import Flow, Tool, FlowExecutor
from agentstable import (
    search,
    get_flow,
    get_and_execute_flow,
    execute_flow
)


class TestToolClass(unittest.TestCase):
    """Test cases for the Tool class."""
    
    def test_tool_init_basic(self):
        """Test basic initialization of a Tool."""
        tool = Tool(
            id="test-tool",
            name="Test Tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}}
        )
        
        self.assertEqual(tool.id, "test-tool")
        self.assertEqual(tool.name, "Test Tool")
        self.assertEqual(tool.description, "A test tool")
        self.assertEqual(tool.parameters, {"type": "object", "properties": {}})
    
    def test_tool_init_openai_format(self):
        """Test initialization of a Tool from OpenAI format."""
        openai_tool = {
            "type": "function",
            "function": {
                "name": "search_wikipedia",
                "description": "Search for information on Wikipedia",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
        
        tool = Tool(**openai_tool)
        
        self.assertEqual(tool.id, "search_wikipedia")
        self.assertEqual(tool.name, "search_wikipedia")
        self.assertEqual(tool.description, "Search for information on Wikipedia")
        self.assertEqual(tool.parameters["required"], ["query"])


class TestFlowClass(unittest.TestCase):
    """Test cases for the Flow class."""
    
    def test_flow_init_basic(self):
        """Test basic initialization of a Flow."""
        flow = Flow(
            id="test-flow",
            name="Test Flow",
            description="A test flow",
            provider="test-provider"
        )
        
        self.assertEqual(flow.id, "test-flow")
        self.assertEqual(flow.name, "Test Flow")
        self.assertEqual(flow.description, "A test flow")
        self.assertEqual(flow.provider, "test-provider")
        self.assertEqual(flow.tools, [])
        self.assertEqual(flow.links, [])
    
    def test_flow_with_tools(self):
        """Test flow with tools."""
        tools = [
            {
                "id": "tool1",
                "name": "Tool 1",
                "description": "Tool 1 description",
                "parameters": {}
            },
            {
                "id": "tool2",
                "name": "Tool 2",
                "description": "Tool 2 description",
                "parameters": {}
            }
        ]
        
        flow = Flow(
            id="test-flow",
            name="Test Flow",
            tools=tools
        )
        
        self.assertEqual(len(flow.tools), 2)
        self.assertEqual(flow.tools[0].id, "tool1")
        self.assertEqual(flow.tools[1].name, "Tool 2")
    
    def test_get_tool_by_id(self):
        """Test getting a tool by ID."""
        tools = [
            {
                "id": "tool1",
                "name": "Tool 1",
                "description": "Tool 1 description",
                "parameters": {}
            },
            {
                "id": "tool2",
                "name": "Tool 2",
                "description": "Tool 2 description",
                "parameters": {}
            }
        ]
        
        flow = Flow(
            id="test-flow",
            name="Test Flow",
            tools=tools
        )
        
        tool = flow.get_tool_by_id("tool2")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.id, "tool2")
        
        tool = flow.get_tool_by_id("non-existent")
        self.assertIsNone(tool)


class TestFlowExecutor(unittest.TestCase):
    """Test cases for the FlowExecutor class."""
    
    def test_execute_flow(self):
        """Test executing a simple flow."""
        # Create a mock for the execute_tool function
        mock_execute_tool = MagicMock(side_effect=lambda tool_id, params, auth: {"result": f"Executed {tool_id} with {params}"})
        
        # Create a flow executor with the mock
        executor = FlowExecutor(mock_execute_tool)
        
        # Create a simple flow
        flow = Flow(
            id="test-flow",
            name="Test Flow",
            tools=[
                {
                    "id": "tool1",
                    "name": "Tool 1",
                    "description": "Tool 1 description",
                    "parameters": {}
                }
            ]
        )
        
        # Execute the flow
        results = executor.execute_flow(flow, {"param": "value"})
        
        # Check the results
        self.assertIn("tool1", results)
        self.assertEqual(results["tool1"]["result"], "Executed tool1 with {'param': 'value'}")
        
        # Verify the mock was called correctly
        mock_execute_tool.assert_called_once_with("tool1", {"param": "value"}, None)
    
    def test_execute_flow_with_links(self):
        """Test executing a flow with links between tools."""
        # Create a mock for the execute_tool function
        def mock_execute_side_effect(tool_id, params, auth):
            if tool_id == "tool1":
                return {"output": "Tool 1 output"}
            elif tool_id == "tool2":
                return {"output": f"Tool 2 processed: {params.get('input', 'None')}"}
        
        mock_execute_tool = MagicMock(side_effect=mock_execute_side_effect)
        
        # Create a flow executor with the mock
        executor = FlowExecutor(mock_execute_tool)
        
        # Create a flow with links
        flow = Flow(
            id="test-flow",
            name="Test Flow",
            tools=[
                {
                    "id": "tool1",
                    "name": "Tool 1",
                    "description": "Tool 1 description",
                    "parameters": {}
                },
                {
                    "id": "tool2",
                    "name": "Tool 2",
                    "description": "Tool 2 description",
                    "parameters": {}
                }
            ],
            links=[
                {
                    "source": "tool1",
                    "target": "tool2",
                    "source_parameter": "output",
                    "target_parameter": "input"
                }
            ]
        )
        
        # Execute the flow
        results = executor.execute_flow(flow, {})
        
        # Check the results
        self.assertIn("tool1", results)
        self.assertIn("tool2", results)
        self.assertEqual(results["tool1"]["output"], "Tool 1 output")
        self.assertEqual(results["tool2"]["output"], "Tool 2 processed: Tool 1 output")
        
        # Verify the mock was called correctly
        self.assertEqual(mock_execute_tool.call_count, 2)


@patch('agentstable.client.requests.post')
@patch('agentstable.client.requests.get')
class TestFlowAPIs(unittest.TestCase):
    """Test cases for the flow API methods."""
    
    def test_search(self, mock_get, mock_post):
        """Test searching for flows."""
        # Mock the search response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "flows": [
                {
                    "id": "wikipedia:search",
                    "name": "Wikipedia Search",
                    "description": "Search for information on Wikipedia",
                    "provider": "wikipedia",
                    "tools": []
                }
            ],
            "total": 1,
            "query": "wikipedia"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Call the search function
        results = search("wikipedia", limit=5)
        
        # Verify the results
        self.assertEqual(len(results.flows), 1)
        self.assertEqual(results.flows[0].id, "wikipedia:search")
        self.assertEqual(results.total, 1)
        self.assertEqual(results.query, "wikipedia")
    
    def test_get_flow(self, mock_get, mock_post):
        """Test getting a flow by ID."""
        # Mock the get_tools_json response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "type": "function",
                "function": {
                    "name": "search_wikipedia",
                    "description": "Search for information on Wikipedia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the get_flow function
        flow = get_flow("wikipedia:search")
        
        # Verify the results
        self.assertEqual(flow.id, "wikipedia:search")
        self.assertEqual(flow.name, "search")
        self.assertEqual(flow.provider, "wikipedia")
        self.assertEqual(len(flow.tools), 1)
        self.assertEqual(flow.tools[0].name, "search_wikipedia")
    
    def test_get_and_execute_flow(self, mock_get, mock_post):
        """Test getting and executing a flow."""
        # Mock the get_tools_json response
        tools_response = MagicMock()
        tools_response.json.return_value = [
            {
                "type": "function",
                "function": {
                    "name": "search_wikipedia",
                    "description": "Search for information on Wikipedia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        tools_response.raise_for_status.return_value = None
        
        # Mock the execute response
        execute_response = MagicMock()
        execute_response.json.return_value = {
            "results": [
                {
                    "title": "Artificial Intelligence",
                    "summary": "AI is...",
                    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
                }
            ]
        }
        execute_response.raise_for_status.return_value = None
        
        # Set up the mock to return different responses for different calls
        mock_get.return_value = tools_response
        mock_post.return_value = execute_response
        
        # Call the get_and_execute_flow function
        results = get_and_execute_flow("wikipedia:search", {"query": "AI"})
        
        # Verify the results
        self.assertIn("search_wikipedia", results)
        self.assertEqual(len(results["search_wikipedia"]["results"]), 1)
        self.assertEqual(results["search_wikipedia"]["results"][0]["title"], "Artificial Intelligence")


if __name__ == "__main__":
    unittest.main() 
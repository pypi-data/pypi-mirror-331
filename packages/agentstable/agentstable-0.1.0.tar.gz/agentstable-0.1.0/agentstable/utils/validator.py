import json
import os
import jsonschema
from typing import Any, Dict

# Basic agents.json schema for validation
AGENTS_JSON_SCHEMA = {
    "type": "object",
    "required": ["provider", "flows"],
    "properties": {
        "provider": {"type": "string"},
        "provider_id": {"type": "string"},
        "version": {"type": "string"},
        "flows": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "description", "tools"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "tools": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "description", "input_schema"],
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "input_schema": {
                                    "type": "object",
                                    "required": ["type", "properties"],
                                    "properties": {
                                        "type": {"type": "string"},
                                        "properties": {"type": "object"},
                                        "required": {
                                            "type": "array", 
                                            "items": {"type": "string"}
                                        }
                                    }
                                },
                                "authentication": {
                                    "type": "object",
                                    "required": ["type"],
                                    "properties": {
                                        "type": {"type": "string"},
                                        "description": {"type": "string"},
                                        "parameters": {"type": "object"}
                                    }
                                },
                                "service_provider": {"type": "string"}
                            }
                        }
                    },
                    "links": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["source", "target", "source_field", "target_field"],
                            "properties": {
                                "source": {"type": "string"},
                                "target": {"type": "string"},
                                "source_field": {"type": "string"},
                                "target_field": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    },
                    "provider": {"type": "string"}
                }
            }
        }
    }
}

class AgentsJSONValidator:
    """Validator for agents.json files."""
    
    def __init__(self, schema: Dict = None):
        """
        Initialize the validator.
        
        Args:
            schema: Optional custom schema to validate against
        """
        self.schema = schema or AGENTS_JSON_SCHEMA
    
    def validate(self, data: Dict) -> bool:
        """
        Validate an agents.json dict against the schema.
        
        Args:
            data: Dict containing agents.json data
            
        Returns:
            True if valid, raises exception if invalid
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid agents.json: {e}")
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate an agents.json file against the schema.
        
        Args:
            file_path: Path to the agents.json file
            
        Returns:
            True if valid, raises exception if invalid
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.validate(data)
    
    def is_valid(self, data: Dict) -> bool:
        """
        Check if an agents.json dict is valid.
        
        Args:
            data: Dict containing agents.json data
            
        Returns:
            True if valid, False if invalid
        """
        try:
            self.validate(data)
            return True
        except:
            return False
    
    def is_file_valid(self, file_path: str) -> bool:
        """
        Check if an agents.json file is valid.
        
        Args:
            file_path: Path to the agents.json file
            
        Returns:
            True if valid, False if invalid
        """
        try:
            self.validate_file(file_path)
            return True
        except:
            return False

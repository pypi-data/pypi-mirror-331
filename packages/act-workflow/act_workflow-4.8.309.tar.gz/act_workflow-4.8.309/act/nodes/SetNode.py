"""
Set Node - Manipulates data by setting, transforming, and deleting values.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable
import asyncio
import re
import copy

from base_node import (
    BaseNode, NodeSchema, NodeParameter, NodeResource, NodeOperation,
    NodeParameterType, NodeOperationType, NodeResourceType,
    NodeValidationError, NodeExecutionError
)


# Configure logging
logger = logging.getLogger(__name__)

class SetOperationType:
    """Set operation types."""
    SET = "set"
    DELETE = "delete"
    TRANSFORM = "transform"
    RENAME = "rename"
    COPY = "copy"
    MERGE = "merge"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    CONCAT = "concat"
    SPLIT = "split"
    FORMAT = "format"
    PARSE = "parse"

class SetNode(BaseNode):
    """
    Node for manipulating data in workflows.
    Can set, transform, and delete values in the workflow data.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the set node."""
        return NodeSchema(
            node_type="set",
            version="1.0.0",
            description="Manipulates data by setting, transforming, and deleting values",
            parameters=[
                NodeParameter(
                    name="operations",
                    type=NodeParameterType.ARRAY,
                    description="List of operations to perform",
                    required=True
                ),
                NodeParameter(
                    name="input_data",
                    type=NodeParameterType.OBJECT,
                    description="Input data to operate on (defaults to node input if not provided)",
                    required=False
                ),
                NodeParameter(
                    name="merge_with_input",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to merge result with input data",
                    required=False,
                    default=True
                ),
                NodeParameter(
                    name="return_input_on_error",
                    type=NodeParameterType.BOOLEAN,
                    description="Whether to return input data on error",
                    required=False,
                    default=True
                )
            ],
            
            # Define resources used by this node
            resources=[
                NodeResource(
                    name="expression_engine",
                    type=NodeResourceType.COMPUTE,
                    description="Engine for evaluating expressions in transform operations",
                    required=False,
                    configuration_parameters=[]
                ),
                NodeResource(
                    name="parser_engine",
                    type=NodeResourceType.COMPUTE,
                    description="Engine for parsing strings in parse operations",
                    required=False,
                    configuration_parameters=[]
                ),
                NodeResource(
                    name="template_engine",
                    type=NodeResourceType.COMPUTE,
                    description="Engine for formatting templates in format operations",
                    required=False,
                    configuration_parameters=[]
                )
            ],
            
            # Define operations provided by this node
            operations=[
                NodeOperation(
                    name="set_value",
                    type=NodeOperationType.UPDATE,
                    description="Set a value at a specified path",
                    required_parameters=["path", "value"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="delete_value",
                    type=NodeOperationType.DELETE,
                    description="Delete a value at a specified path",
                    required_parameters=["path"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="transform_value",
                    type=NodeOperationType.TRANSFORM,
                    description="Transform a value using an expression",
                    required_parameters=["path", "expression"],
                    required_resources=["expression_engine"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="rename_path",
                    type=NodeOperationType.UPDATE,
                    description="Rename a path",
                    required_parameters=["path", "new_path"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="copy_value",
                    type=NodeOperationType.CREATE,
                    description="Copy a value from one path to another",
                    required_parameters=["path", "target_path"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="merge_data",
                    type=NodeOperationType.UPDATE,
                    description="Merge data with existing data",
                    required_parameters=["data"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="increment_value",
                    type=NodeOperationType.UPDATE,
                    description="Increment a numeric value",
                    required_parameters=["path", "amount"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="format_string",
                    type=NodeOperationType.TRANSFORM,
                    description="Format a string using a template",
                    required_parameters=["path", "template"],
                    required_resources=["template_engine"],
                    produces={"result": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="parse_string",
                    type=NodeOperationType.TRANSFORM,
                    description="Parse a string using a format",
                    required_parameters=["path", "format"],
                    required_resources=["parser_engine"],
                    produces={"result": NodeParameterType.OBJECT}
                )
            ],
            
            outputs={
                "result": NodeParameterType.OBJECT,
                "status": NodeParameterType.STRING,
                "operation_count": NodeParameterType.NUMBER,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["data-manipulation", "transformation", "object"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for operations."""
        params = node_data.get("params", {})
        operations = params.get("operations", [])
        
        if not operations or not isinstance(operations, list):
            raise NodeValidationError("Operations must be a non-empty array")
        
        for i, operation in enumerate(operations):
            if not isinstance(operation, dict):
                raise NodeValidationError(f"Operation at index {i} must be an object")
                
            operation_type = operation.get("type")
            if not operation_type:
                raise NodeValidationError(f"Operation at index {i} must have a type")
                
            path = operation.get("path")
            if not path and operation_type != SetOperationType.MERGE:
                raise NodeValidationError(f"Operation at index {i} must have a path")
                
            # Validate based on operation type
            if operation_type == SetOperationType.SET:
                if "value" not in operation:
                    raise NodeValidationError(f"SET operation at index {i} must have a value")
                    
            elif operation_type == SetOperationType.TRANSFORM:
                if "expression" not in operation:
                    raise NodeValidationError(f"TRANSFORM operation at index {i} must have an expression")
                    
            elif operation_type == SetOperationType.RENAME:
                if "new_path" not in operation:
                    raise NodeValidationError(f"RENAME operation at index {i} must have a new_path")
                    
            elif operation_type == SetOperationType.COPY:
                if "target_path" not in operation:
                    raise NodeValidationError(f"COPY operation at index {i} must have a target_path")
                    
            elif operation_type == SetOperationType.MERGE:
                if "data" not in operation:
                    raise NodeValidationError(f"MERGE operation at index {i} must have data")
                    
            elif operation_type == SetOperationType.INCREMENT or operation_type == SetOperationType.DECREMENT:
                if "amount" not in operation:
                    raise NodeValidationError(f"{operation_type} operation at index {i} must have an amount")
                    
            elif operation_type == SetOperationType.CONCAT:
                if "value" not in operation:
                    raise NodeValidationError(f"CONCAT operation at index {i} must have a value")
                    
            elif operation_type == SetOperationType.SPLIT:
                if "delimiter" not in operation:
                    raise NodeValidationError(f"SPLIT operation at index {i} must have a delimiter")
                    
            elif operation_type == SetOperationType.FORMAT:
                if "template" not in operation:
                    raise NodeValidationError(f"FORMAT operation at index {i} must have a template")
                    
            elif operation_type == SetOperationType.PARSE:
                if "format" not in operation:
                    raise NodeValidationError(f"PARSE operation at index {i} must have a format")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the set node operations."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get input data
            input_data = validated_data.get("input_data")
            if input_data is None:
                input_data = node_data.get("input", {})
            
            # Make a deep copy of the input data to avoid modifying the original
            data = copy.deepcopy(input_data)
            
            # Get operations
            operations = validated_data["operations"]
            
            # Apply each operation
            operation_errors = []
            for i, operation in enumerate(operations):
                try:
                    await self.operation_apply(operation, data, node_data)
                except Exception as e:
                    error_msg = f"Error in operation {i} ({operation.get('type')}): {str(e)}"
                    operation_errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Stop on first error if requested
                    if operation.get("stop_on_error", False):
                        break
            
            # Check if we should merge with input
            if validated_data.get("merge_with_input", True):
                # Create a deep merge of input and result
                result = self.operation_deep_merge(input_data, data)
            else:
                result = data
            
            # Return the result
            status = "success" if not operation_errors else "warning"
            return {
                "result": result,
                "status": status,
                "operation_count": len(operations),
                "error": "; ".join(operation_errors) if operation_errors else None
            }
            
        except Exception as e:
            error_message = f"Error in set node: {str(e)}"
            logger.error(error_message)
            
            # Return input data on error if requested
            if validated_data.get("return_input_on_error", True):
                return {
                    "result": input_data if 'input_data' in locals() else node_data.get("input", {}),
                    "status": "error",
                    "operation_count": 0,
                    "error": error_message
                }
            else:
                return {
                    "result": {},
                    "status": "error",
                    "operation_count": 0,
                    "error": error_message
                }
    
    # -------------------------
    # Operation Methods
    # -------------------------
    
    async def operation_apply(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Apply a single operation to the data.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        operation_type = operation["type"]
        
        if operation_type == SetOperationType.SET:
            await self.operation_set_value(operation, data, node_data)
            
        elif operation_type == SetOperationType.DELETE:
            self.operation_delete_value(operation, data)
            
        elif operation_type == SetOperationType.TRANSFORM:
            await self.operation_transform_value(operation, data, node_data)
            
        elif operation_type == SetOperationType.RENAME:
            self.operation_rename_path(operation, data)
            
        elif operation_type == SetOperationType.COPY:
            self.operation_copy_value(operation, data)
            
        elif operation_type == SetOperationType.MERGE:
            await self.operation_merge_data(operation, data, node_data)
            
        elif operation_type == SetOperationType.INCREMENT:
            self.operation_increment_value(operation, data)
            
        elif operation_type == SetOperationType.DECREMENT:
            self.operation_decrement_value(operation, data)
            
        elif operation_type == SetOperationType.CONCAT:
            await self.operation_concat_string(operation, data, node_data)
            
        elif operation_type == SetOperationType.SPLIT:
            self.operation_split_string(operation, data)
            
        elif operation_type == SetOperationType.FORMAT:
            await self.operation_format_string(operation, data, node_data)
            
        elif operation_type == SetOperationType.PARSE:
            await self.operation_parse_string(operation, data)
            
        else:
            logger.warning(f"Unknown operation type: {operation_type}")
    
    async def operation_set_value(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Set a value at a path.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        path = operation["path"]
        value = operation["value"]
        
        # Resolve any placeholders in the value
        resolved_value = self._resolve_value(value, node_data)
        
        # Set the value
        self._set_value_at_path(data, path, resolved_value, create_missing=operation.get("create_missing", True))
    
    def operation_delete_value(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Delete a value at a path.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        
        # Delete the value
        self._delete_value_at_path(data, path)
    
    async def operation_transform_value(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Transform a value using an expression.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        path = operation["path"]
        expression = operation["expression"]
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Create a context with the current value and node data
        context = {
            "value": current_value,
            "data": data,
            "input": node_data.get("input", {}),
            "params": node_data.get("params", {})
        }
        
        # Check if we have an expression engine resource
        expression_engine = self.resources.get("expression_engine")
        if expression_engine and hasattr(expression_engine, 'evaluate_expression'):
            try:
                result = await self._execute_async_if_needed(
                    expression_engine.evaluate_expression,
                    expression,
                    context
                )
            except Exception as e:
                logger.error(f"Error evaluating expression with engine: {str(e)}")
                raise
        else:
            # Evaluate the expression using built-in eval
            try:
                result = eval(expression, {"__builtins__": {}}, context)
            except Exception as e:
                logger.error(f"Error evaluating transform expression: {str(e)}")
                raise
        
        # Set the transformed value
        self._set_value_at_path(data, path, result)
    
    def operation_rename_path(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Rename a path.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        new_path = operation["new_path"]
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Set the value at the new path
        self._set_value_at_path(data, new_path, current_value, create_missing=operation.get("create_missing", True))
        
        # Delete the old path if requested
        if operation.get("delete_original", True):
            self._delete_value_at_path(data, path)
    
    def operation_copy_value(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Copy a value from one path to another.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        target_path = operation["target_path"]
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Make a deep copy to avoid reference issues
        copied_value = copy.deepcopy(current_value)
        
        # Set the value at the target path
        self._set_value_at_path(data, target_path, copied_value, create_missing=operation.get("create_missing", True))
    
    async def operation_merge_data(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Merge an object with the data.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        merge_data = operation["data"]
        path = operation.get("path", "")
        
        # Resolve any placeholders in the merge data
        resolved_data = self._resolve_value(merge_data, node_data)
        
        if path:
            # Get the target object
            target = self._get_value_at_path(data, path)
            
            # Ensure the target is an object
            if not isinstance(target, dict):
                target = {}
                self._set_value_at_path(data, path, target)
            
            # Merge the data
            merged = self.operation_deep_merge(target, resolved_data)
            
            # Set the merged result
            self._set_value_at_path(data, path, merged)
        else:
            # Merge with the root object
            self._deep_merge_inplace(data, resolved_data)
    
    def operation_increment_value(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Increment a numeric value.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        amount = operation["amount"]
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Ensure the current value is numeric
        if current_value is None:
            current_value = 0
        elif not isinstance(current_value, (int, float)):
            try:
                current_value = float(current_value)
            except (ValueError, TypeError):
                current_value = 0
        
        # Increment the value
        try:
            new_value = current_value + amount
        except TypeError:
            # Handle cases where current_value or amount is not numeric
            logger.error(f"Cannot increment: current value ({current_value}) or amount ({amount}) is not numeric")
            new_value = current_value
        
        # Set the new value
        self._set_value_at_path(data, path, new_value, create_missing=operation.get("create_missing", True))
    
    def operation_decrement_value(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Decrement a numeric value.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        # Decrement is just increment with a negative amount
        operation = operation.copy()
        operation["amount"] = -operation["amount"]
        self.operation_increment_value(operation, data)
    
    async def operation_concat_string(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Concatenate a string to a value.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        path = operation["path"]
        value = operation["value"]
        
        # Resolve any placeholders in the value
        resolved_value = self._resolve_value(value, node_data)
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Ensure the current value is a string
        if current_value is None:
            current_value = ""
        elif not isinstance(current_value, str):
            current_value = str(current_value)
        
        # Concatenate the value
        new_value = current_value + str(resolved_value)
        
        # Set the new value
        self._set_value_at_path(data, path, new_value, create_missing=operation.get("create_missing", True))
    
    def operation_split_string(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Split a string into an array.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        delimiter = operation["delimiter"]
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Ensure the current value is a string
        if current_value is None:
            current_value = ""
        elif not isinstance(current_value, str):
            current_value = str(current_value)
        
        # Split the string
        new_value = current_value.split(delimiter)
        
        # Set the new value
        self._set_value_at_path(data, path, new_value, create_missing=operation.get("create_missing", True))
    
    async def operation_format_string(self, operation: Dict[str, Any], data: Dict[str, Any], node_data: Dict[str, Any]) -> None:
        """
        Format a string using a template.
        
        Args:
            operation: Operation definition
            data: Data to modify
            node_data: Original node data for context
        """
        path = operation["path"]
        template = operation["template"]
        
        # Get context for formatting
        context = {
            "data": data,
            "input": node_data.get("input", {}),
            "params": node_data.get("params", {})
        }
        
        # Check if we have a template engine resource
        template_engine = self.resources.get("template_engine")
        if template_engine and hasattr(template_engine, 'render_template'):
            try:
                result = await self._execute_async_if_needed(
                    template_engine.render_template,
                    template,
                    context
                )
            except Exception as e:
                logger.error(f"Error rendering template with engine: {str(e)}")
                raise
        else:
            # Use simple string format
            try:
                # Resolve placeholders in the template
                resolved_template = self.resolve_placeholders(template, node_data)
                
                # Try to format using the context directly
                result = resolved_template.format(**context)
            except KeyError as e:
                logger.error(f"Missing key in template: {str(e)}")
                result = resolved_template
            except Exception as e:
                logger.error(f"Error formatting template: {str(e)}")
                result = resolved_template
        
        # Set the formatted value
        self._set_value_at_path(data, path, result, create_missing=operation.get("create_missing", True))
    
    async def operation_parse_string(self, operation: Dict[str, Any], data: Dict[str, Any]) -> None:
        """
        Parse a string using a format.
        
        Args:
            operation: Operation definition
            data: Data to modify
        """
        path = operation["path"]
        format_spec = operation["format"]
        target_path = operation.get("target_path", path)
        
        # Get the current value
        current_value = self._get_value_at_path(data, path)
        
        # Ensure the current value is a string
        if current_value is None:
            current_value = ""
        elif not isinstance(current_value, str):
            current_value = str(current_value)
        
        # Check if we have a parser engine resource
        parser_engine = self.resources.get("parser_engine")
        if parser_engine and hasattr(parser_engine, 'parse_string'):
            try:
                result = await self._execute_async_if_needed(
                    parser_engine.parse_string,
                    current_value,
                    format_spec
                )
            except Exception as e:
                logger.error(f"Error parsing string with engine: {str(e)}")
                raise
        else:
            # Simple parsing based on format
            try:
                # Very basic parsing for common formats
                if format_spec == "json":
                    result = json.loads(current_value)
                elif format_spec == "csv":
                    # Simple CSV parsing
                    lines = current_value.strip().split("\n")
                    if not lines:
                        result = []
                    else:
                        headers = lines[0].split(",")
                        result = []
                        for line in lines[1:]:
                            values = line.split(",")
                            row = {}
                            for i, header in enumerate(headers):
                                if i < len(values):
                                    row[header] = values[i]
                                else:
                                    row[header] = ""
                            result.append(row)
                else:
                    # Unknown format
                    logger.warning(f"Unknown parse format: {format_spec}")
                    result = current_value
            except Exception as e:
                logger.error(f"Error parsing string: {str(e)}")
                result = current_value
        
        # Set the parsed value
        self._set_value_at_path(data, target_path, result, create_missing=operation.get("create_missing", True))

    def operation_deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a deep merge of two dictionaries.
        
        Args:
            target: Target dictionary
            source: Source dictionary
            
        Returns:
            Merged dictionary
        """
        # Create a copy of the target
        result = copy.deepcopy(target)
        
        # Perform the merge
        self._deep_merge_inplace(result, source)
        
        return result
    
    # -------------------------
    # Helper Methods
    # -------------------------
    
    def _deep_merge_inplace(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Perform a deep merge of two dictionaries in place.
        
        Args:
            target: Target dictionary to modify
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self._deep_merge_inplace(target[key], value)
            else:
                # Copy or overwrite the value
                target[key] = copy.deepcopy(value)
    
    def _get_value_at_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a value at a path in a nested dictionary.
        
        Args:
            data: Dictionary to navigate
            path: Path to the value, using dot notation
            
        Returns:
            Value at the path, or None if not found
        """
        if not path:
            return data
            
        parts = path.split(".")
        current = data
        
        for part in parts:
            # Handle array indices in path (e.g., items[0].name)
            match = re.match(r"([^\[]+)\[(\d+)\]", part)
            if match:
                # Extract array name and index
                array_name = match.group(1)
                index = int(match.group(2))
                
                # Navigate to the array
                if array_name in current and isinstance(current[array_name], list):
                    current = current[array_name]
                    # Check if index is valid
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            else:
                # Normal object property
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
        
        return current
    
    def _set_value_at_path(self, data: Dict[str, Any], path: str, value: Any, create_missing: bool = True) -> None:
        """
        Set a value at a path in a nested dictionary.
        
        Args:
            data: Dictionary to modify
            path: Path to set the value at, using dot notation
            value: Value to set
            create_missing: Whether to create missing intermediate objects
        """
        if not path:
            # Can't set at root level
            return
            
        parts = path.split(".")
        current = data
        
        # Navigate to the parent
        for i, part in enumerate(parts[:-1]):
            # Handle array indices in path (e.g., items[0].name)
            match = re.match(r"([^\[]+)\[(\d+)\]", part)
            if match:
                # Extract array name and index
                array_name = match.group(1)
                index = int(match.group(2))
                
                # Ensure parent exists
                if array_name not in current:
                    if create_missing:
                        current[array_name] = []
                    else:
                        return
                
                # Ensure parent is a list
                if not isinstance(current[array_name], list):
                    if create_missing:
                        current[array_name] = []
                    else:
                        return
                
                # Ensure list is long enough
                while len(current[array_name]) <= index:
                    if create_missing:
                        current[array_name].append({})
                    else:
                        return
                
                # Navigate to the array element
                current = current[array_name][index]
            else:
                # Normal object property
                if part not in current:
                    if create_missing:
                        current[part] = {}
                    else:
                        return
                
                # Navigate to the next level
                current = current[part]
        
        # Set the value at the leaf
        leaf = parts[-1]
        
        # Handle array indices in leaf (e.g., items[0])
        match = re.match(r"([^\[]+)\[(\d+)\]", leaf)
        if match:
            # Extract array name and index
            array_name = match.group(1)
            index = int(match.group(2))
            
            # Ensure array exists
            if array_name not in current:
                if create_missing:
                    current[array_name] = []
                else:
                    return
            
            # Ensure it's a list
            if not isinstance(current[array_name], list):
                if create_missing:
                    current[array_name] = []
                else:
                    return
            
            # Ensure list is long enough
            while len(current[array_name]) <= index:
                if create_missing:
                    current[array_name].append(None)
                else:
                    return
            
            # Set the value at the index
            current[array_name][index] = value
        else:
            # Normal object property
            current[leaf] = value
    
    def _delete_value_at_path(self, data: Dict[str, Any], path: str) -> None:
        """
        Delete a value at a path in a nested dictionary.
        
        Args:
            data: Dictionary to modify
            path: Path to delete the value at, using dot notation
        """
        if not path:
            # Can't delete the root
            return
            
        parts = path.split(".")
        current = data
        
        # Navigate to the parent
        for i, part in enumerate(parts[:-1]):
            # Handle array indices in path (e.g., items[0].name)
            match = re.match(r"([^\[]+)\[(\d+)\]", part)
            if match:
                # Extract array name and index
                array_name = match.group(1)
                index = int(match.group(2))
                
                # Check if the parent exists
                if array_name not in current or not isinstance(current[array_name], list):
                    return
                
                # Check if the index is valid
                if index >= len(current[array_name]):
                    return
                
                # Navigate to the array element
                current = current[array_name][index]
            else:
                # Normal object property
                if part not in current or not isinstance(current, dict):
                    return
                
                # Navigate to the next level
                current = current[part]
        
        # Delete the value at the leaf
        leaf = parts[-1]
        
        # Handle array indices in leaf (e.g., items[0])
        match = re.match(r"([^\[]+)\[(\d+)\]", leaf)
        if match:
            # Extract array name and index
            array_name = match.group(1)
            index = int(match.group(2))
            
            # Check if the array exists
            if array_name not in current or not isinstance(current[array_name], list):
                return
            
            # Check if the index is valid
            if index < len(current[array_name]):
                # Set the element to None (don't remove it to maintain indices)
                current[array_name][index] = None
        else:
            # Normal object property
            if leaf in current:
                del current[leaf]
    
    def _resolve_value(self, value: Any, node_data: Dict[str, Any]) -> Any:
        """
        Resolve placeholders in a value.
        
        Args:
            value: The value to resolve
            node_data: Node data for resolving placeholders
            
        Returns:
            Resolved value
        """
        if isinstance(value, str):
            return self.resolve_placeholders(value, node_data)
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, node_data) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_value(item, node_data) for item in value]
        else:
            return value
    
    async def _execute_async_if_needed(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function asynchronously if it's a coroutine function,
        otherwise execute it synchronously.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Function result
        """
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("set", SetNode)
    logger.info("Successfully registered SetNode with registry")
except ImportError:
    logger.warning("Could not register SetNode with registry - module not found")
except Exception as e:
    logger.error(f"Error registering SetNode with registry: {str(e)}")
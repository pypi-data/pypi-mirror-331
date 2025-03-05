"""
If Node - Conditional branching node for workflows.
Evaluates a condition and directs flow to one of two paths.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
import asyncio
import re

from base_node import (
    BaseNode, NodeSchema, NodeParameter, NodeResource, NodeOperation,
    NodeParameterType, NodeOperationType, NodeResourceType,
    NodeValidationError, NodeExecutionError
)

# Configure logging
logger = logging.getLogger(__name__)

class ComparisonOperator:
    """Comparison operators for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUALS = "greater_than_or_equals"
    LESS_THAN_OR_EQUALS = "less_than_or_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES_REGEX = "matches_regex"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IN = "in"
    NOT_IN = "not_in"

class LogicalOperator:
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"

class IfNode(BaseNode):
    """
    Node for conditional branching in workflows.
    Evaluates a condition and directs workflow to either true or false branch.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.execution_manager = None
    
    def set_execution_manager(self, execution_manager):
        """Set the execution manager for this node."""
        self.execution_manager = execution_manager
        logger.debug("Set execution manager for IfNode")
    
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the if node."""
        return NodeSchema(
            node_type="if",
            version="1.0.0",
            description="Evaluates a condition and branches workflow execution",
            # Define all parameters
            parameters=[
                # Main condition parameters
                NodeParameter(
                    name="condition_type",
                    type=NodeParameterType.STRING,
                    description="Type of condition to evaluate",
                    required=True,
                    enum=["simple", "advanced", "expression", "script"]
                ),
                
                # Simple condition parameters
                NodeParameter(
                    name="left_value",
                    type=NodeParameterType.ANY,
                    description="Left value for comparison (for simple condition)",
                    required=False
                ),
                NodeParameter(
                    name="operator",
                    type=NodeParameterType.STRING,
                    description="Comparison operator (for simple condition)",
                    required=False,
                    enum=[
                        ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS,
                        ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN,
                        ComparisonOperator.GREATER_THAN_OR_EQUALS, ComparisonOperator.LESS_THAN_OR_EQUALS,
                        ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS,
                        ComparisonOperator.STARTS_WITH, ComparisonOperator.ENDS_WITH,
                        ComparisonOperator.MATCHES_REGEX, ComparisonOperator.IS_NULL,
                        ComparisonOperator.IS_NOT_NULL, ComparisonOperator.IS_EMPTY,
                        ComparisonOperator.IS_NOT_EMPTY, ComparisonOperator.IN,
                        ComparisonOperator.NOT_IN
                    ]
                ),
                NodeParameter(
                    name="right_value",
                    type=NodeParameterType.ANY,
                    description="Right value for comparison (for simple condition)",
                    required=False
                ),
                
                # Advanced condition parameters
                NodeParameter(
                    name="conditions",
                    type=NodeParameterType.ARRAY,
                    description="List of conditions to combine (for advanced condition)",
                    required=False
                ),
                NodeParameter(
                    name="logical_operator",
                    type=NodeParameterType.STRING,
                    description="Logical operator to combine conditions (for advanced condition)",
                    required=False,
                    enum=[LogicalOperator.AND, LogicalOperator.OR, LogicalOperator.NOT],
                    default=LogicalOperator.AND
                ),
                
                # Expression condition parameters
                NodeParameter(
                    name="expression",
                    type=NodeParameterType.STRING,
                    description="Expression to evaluate (for expression condition)",
                    required=False
                ),
                
                # Script condition parameters
                NodeParameter(
                    name="script",
                    type=NodeParameterType.STRING,
                    description="Script to evaluate (for script condition)",
                    required=False
                ),
                NodeParameter(
                    name="script_language",
                    type=NodeParameterType.STRING,
                    description="Language of the script (for script condition)",
                    required=False,
                    enum=["javascript", "python"],
                    default="javascript"
                ),
                
                # Output routing parameters
                NodeParameter(
                    name="true_branch",
                    type=NodeParameterType.STRING,
                    description="Node to execute if condition is true",
                    required=False
                ),
                NodeParameter(
                    name="false_branch",
                    type=NodeParameterType.STRING,
                    description="Node to execute if condition is false",
                    required=False
                ),
                
                # Data transformation parameters
                NodeParameter(
                    name="transform_true_data",
                    type=NodeParameterType.OBJECT,
                    description="Data transformations to apply if condition is true",
                    required=False
                ),
                NodeParameter(
                    name="transform_false_data",
                    type=NodeParameterType.OBJECT,
                    description="Data transformations to apply if condition is false",
                    required=False
                )
            ],
            
            # Define resources used by this node
            resources=[
                NodeResource(
                    name="script_engine",
                    type=NodeResourceType.COMPUTE,
                    description="Script engine for evaluating script conditions",
                    required=False,
                    configuration_parameters=["script_language"]
                ),
                NodeResource(
                    name="context_data",
                    type=NodeResourceType.MEMORY,
                    description="Additional context data for condition evaluation",
                    required=False
                )
            ],
            
            # Define operations provided by this node
            operations=[
                NodeOperation(
                    name="evaluate_condition",
                    type=NodeOperationType.CONDITION,
                    description="Evaluate the specified condition",
                    required_parameters=["condition_type"],
                    produces={"result": NodeParameterType.BOOLEAN}
                ),
                NodeOperation(
                    name="transform_data",
                    type=NodeOperationType.TRANSFORM,
                    description="Transform data based on condition result",
                    required_parameters=["transform_true_data", "transform_false_data"],
                    produces={"transformed_data": NodeParameterType.OBJECT}
                ),
                NodeOperation(
                    name="determine_branch",
                    type=NodeOperationType.CONDITION,
                    description="Determine which branch to follow",
                    required_parameters=["true_branch", "false_branch"],
                    produces={"branch": NodeParameterType.STRING}
                )
            ],
            
            # Define outputs for the node
            outputs={
                "result": NodeParameterType.BOOLEAN,
                "branch": NodeParameterType.STRING,
                "status": NodeParameterType.STRING,
                "transformed_data": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING
            },
            
            # Add metadata
            tags=["control-flow", "conditional", "branching"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the condition type."""
        params = node_data.get("params", {})
        condition_type = params.get("condition_type")
        
        if not condition_type:
            raise NodeValidationError("Condition type is required")
        
        # Validate based on condition type
        if condition_type == "simple":
            if params.get("left_value") is None:
                raise NodeValidationError("Left value is required for simple condition")
                
            if not params.get("operator"):
                raise NodeValidationError("Operator is required for simple condition")
                
            # Right value is optional for some operators (IS_NULL, IS_NOT_NULL, etc.)
            if params.get("operator") not in [
                ComparisonOperator.IS_NULL, ComparisonOperator.IS_NOT_NULL,
                ComparisonOperator.IS_EMPTY, ComparisonOperator.IS_NOT_EMPTY
            ] and params.get("right_value") is None:
                raise NodeValidationError("Right value is required for this operator")
                
        elif condition_type == "advanced":
            if not params.get("conditions") or not isinstance(params.get("conditions"), list):
                raise NodeValidationError("Conditions array is required for advanced condition")
                
            if not params.get("logical_operator"):
                raise NodeValidationError("Logical operator is required for advanced condition")
                
        elif condition_type == "expression":
            if not params.get("expression"):
                raise NodeValidationError("Expression is required for expression condition")
                
        elif condition_type == "script":
            if not params.get("script"):
                raise NodeValidationError("Script is required for script condition")
                
            if not params.get("script_language"):
                raise NodeValidationError("Script language is required for script condition")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the if node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # First operation: Evaluate the condition
            result = await self.operation_evaluate_condition_async(validated_data, node_data)
            
            # Second operation: Determine branch
            branch_name = self.operation_determine_branch(result, validated_data)
            
            # Third operation: Transform data
            transformed_data = self.operation_transform_data(result, validated_data, node_data)
            
            # Return the result
            return {
                "status": "success",
                "result": result,
                "branch": branch_name,
                "transformed_data": transformed_data,
                "error": None
            }
            
        except Exception as e:
            error_message = f"Error in if node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "branch": None,
                "transformed_data": {},
                "error": error_message
            }
    
    # -------------------------
    # Operation Implementations
    # -------------------------
    
    async def operation_evaluate_condition_async(self, validated_data: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Async implementation of evaluate_condition operation.
        
        Args:
            validated_data: Validated parameters
            node_data: Full node data for context and resolving placeholders
            
        Returns:
            Boolean result of the condition
        """
        condition_type = validated_data["condition_type"]
        
        # Evaluate based on condition type
        if condition_type == "simple":
            return self._evaluate_simple_condition(validated_data, node_data)
        elif condition_type == "advanced":
            return await self._evaluate_advanced_condition(validated_data, node_data)
        elif condition_type == "expression":
            return self._evaluate_expression_condition(validated_data, node_data)
        elif condition_type == "script":
            return self._evaluate_script_condition(validated_data, node_data)
        else:
            raise NodeValidationError(f"Unknown condition type: {condition_type}")
    
    def operation_evaluate_condition(self, node_data: Dict[str, Any]) -> bool:
        """
        Sync version of evaluate_condition operation.
        
        Args:
            node_data: Node data for execution
            
        Returns:
            Boolean result of the condition
        """
        loop = asyncio.new_event_loop()
        try:
            validated_data = self.validate_schema(node_data)
            return loop.run_until_complete(self.operation_evaluate_condition_async(validated_data, node_data))
        finally:
            loop.close()
    
    def operation_determine_branch(self, result: bool, validated_data: Dict[str, Any]) -> Optional[str]:
        """
        Implementation of determine_branch operation.
        
        Args:
            result: Condition result
            validated_data: Validated parameters
            
        Returns:
            Branch name to follow
        """
        branch = "true_branch" if result else "false_branch"
        return validated_data.get(branch)
    
    def operation_transform_data(self, result: bool, validated_data: Dict[str, Any], node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementation of transform_data operation.
        
        Args:
            result: Condition result
            validated_data: Validated parameters
            node_data: Full node data
            
        Returns:
            Transformed data
        """
        transform_key = "transform_true_data" if result else "transform_false_data"
        transformations = validated_data.get(transform_key, {})
        return self._apply_transformations(transformations, node_data)
    
    # -------------------------
    # Helper Methods for Operations
    # -------------------------
    
    def _evaluate_simple_condition(self, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate a simple condition: left_value operator right_value.
        
        Args:
            params: Validated parameters
            node_data: Full node data for context and resolving placeholders
            
        Returns:
            Boolean result of the condition
        """
        operator = params["operator"]
        left_value = self._resolve_value(params["left_value"], node_data)
        
        # Handle operators that don't need a right value
        if operator == ComparisonOperator.IS_NULL:
            return left_value is None
            
        elif operator == ComparisonOperator.IS_NOT_NULL:
            return left_value is not None
            
        elif operator == ComparisonOperator.IS_EMPTY:
            if left_value is None:
                return True
            elif isinstance(left_value, (str, list, dict)):
                return len(left_value) == 0
            return False
            
        elif operator == ComparisonOperator.IS_NOT_EMPTY:
            if left_value is None:
                return False
            elif isinstance(left_value, (str, list, dict)):
                return len(left_value) > 0
            return True
        
        # All other operators need a right value
        right_value = self._resolve_value(params["right_value"], node_data)
        
        # Evaluate based on operator
        if operator == ComparisonOperator.EQUALS:
            return left_value == right_value
            
        elif operator == ComparisonOperator.NOT_EQUALS:
            return left_value != right_value
            
        elif operator == ComparisonOperator.GREATER_THAN:
            return left_value > right_value
            
        elif operator == ComparisonOperator.LESS_THAN:
            return left_value < right_value
            
        elif operator == ComparisonOperator.GREATER_THAN_OR_EQUALS:
            return left_value >= right_value
            
        elif operator == ComparisonOperator.LESS_THAN_OR_EQUALS:
            return left_value <= right_value
            
        elif operator == ComparisonOperator.CONTAINS:
            if left_value is None or right_value is None:
                return False
            
            if isinstance(left_value, str):
                return right_value in left_value
            elif isinstance(left_value, (list, tuple, set)):
                return right_value in left_value
            elif isinstance(left_value, dict):
                return right_value in left_value or right_value in left_value.values()
            
            return False
            
        elif operator == ComparisonOperator.NOT_CONTAINS:
            if left_value is None or right_value is None:
                return True
            
            if isinstance(left_value, str):
                return right_value not in left_value
            elif isinstance(left_value, (list, tuple, set)):
                return right_value not in left_value
            elif isinstance(left_value, dict):
                return right_value not in left_value and right_value not in left_value.values()
            
            return True
            
        elif operator == ComparisonOperator.STARTS_WITH:
            if not isinstance(left_value, str) or not isinstance(right_value, str):
                return False
            return left_value.startswith(right_value)
            
        elif operator == ComparisonOperator.ENDS_WITH:
            if not isinstance(left_value, str) or not isinstance(right_value, str):
                return False
            return left_value.endswith(right_value)
            
        elif operator == ComparisonOperator.MATCHES_REGEX:
            if not isinstance(left_value, str) or not isinstance(right_value, str):
                return False
            
            try:
                pattern = re.compile(right_value)
                return bool(pattern.match(left_value))
            except re.error:
                logger.error(f"Invalid regex pattern: {right_value}")
                return False
                
        elif operator == ComparisonOperator.IN:
            if right_value is None:
                return False
            
            if isinstance(right_value, (list, tuple, set)):
                return left_value in right_value
            elif isinstance(right_value, dict):
                return left_value in right_value
            elif isinstance(right_value, str) and isinstance(left_value, str):
                return left_value in right_value
            
            return False
            
        elif operator == ComparisonOperator.NOT_IN:
            if right_value is None:
                return True
            
            if isinstance(right_value, (list, tuple, set)):
                return left_value not in right_value
            elif isinstance(right_value, dict):
                return left_value not in right_value
            elif isinstance(right_value, str) and isinstance(left_value, str):
                return left_value not in right_value
            
            return True
        
        logger.warning(f"Unknown operator: {operator}")
        return False
    
    async def _evaluate_advanced_condition(self, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate an advanced condition with multiple sub-conditions.
        
        Args:
            params: Validated parameters
            node_data: Full node data for context and resolving placeholders
            
        Returns:
            Boolean result of the condition
        """
        conditions = params["conditions"]
        logical_operator = params["logical_operator"]
        
        if not conditions:
            return False
        
        # Evaluate all sub-conditions
        results = []
        for condition in conditions:
            # Create a nested if node to evaluate the condition
            nested_if_node = IfNode()
            
            # Create a nested node data
            nested_node_data = {
                "params": {
                    "condition_type": condition.get("condition_type", "simple"),
                    "left_value": condition.get("left_value"),
                    "operator": condition.get("operator"),
                    "right_value": condition.get("right_value"),
                    "expression": condition.get("expression"),
                    "script": condition.get("script"),
                    "script_language": condition.get("script_language")
                }
            }
            
            # Add advanced condition parameters if needed
            if condition.get("condition_type") == "advanced":
                nested_node_data["params"]["conditions"] = condition.get("conditions", [])
                nested_node_data["params"]["logical_operator"] = condition.get("logical_operator", LogicalOperator.AND)
            
            # Execute the nested if node asynchronously
            try:
                nested_result = await nested_if_node.execute(nested_node_data)
                results.append(nested_result.get("result", False))
            except Exception as e:
                logger.error(f"Error evaluating nested condition: {str(e)}")
                results.append(False)
        
        # Combine results based on logical operator
        if logical_operator == LogicalOperator.AND:
            return all(results)
        elif logical_operator == LogicalOperator.OR:
            return any(results)
        elif logical_operator == LogicalOperator.NOT:
            # NOT applies to the first condition only
            return not results[0] if results else False
        
        logger.warning(f"Unknown logical operator: {logical_operator}")
        return False
    
    def _evaluate_expression_condition(self, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition using a Python expression.
        
        Args:
            params: Validated parameters
            node_data: Full node data for context and resolving placeholders
            
        Returns:
            Boolean result of the condition
        """
        expression = params["expression"]
        
        try:
            # Create a context with node data
            context = {
                "input": node_data.get("input", {}),
                "params": node_data.get("params", {}),
                "resources": node_data.get("resources", {})
            }
            
            # Check if we have a script engine resource
            script_engine = self.resources.get("script_engine")
            if script_engine and hasattr(script_engine, "eval_expression"):
                return bool(script_engine.eval_expression(expression, context))
            
            # Fall back to built-in eval if no script engine
            # This is not secure! In a real system, use a sandbox
            result = eval(expression, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            return False
    
    def _evaluate_script_condition(self, params: Dict[str, Any], node_data: Dict[str, Any]) -> bool:
        """
        Evaluate a condition using a script.
        
        Args:
            params: Validated parameters
            node_data: Full node data for context and resolving placeholders
            
        Returns:
            Boolean result of the condition
        """
        script = params["script"]
        script_language = params["script_language"]
        
        # Check if we have a script engine resource
        script_engine = self.resources.get("script_engine")
        if script_engine and hasattr(script_engine, "eval_script"):
            try:
                # Create a context with node data
                context = {
                    "input": node_data.get("input", {}),
                    "params": node_data.get("params", {}),
                    "resources": node_data.get("resources", {})
                }
                
                # Execute the script using the engine
                result = script_engine.eval_script(script, script_language, context)
                return bool(result)
            except Exception as e:
                logger.error(f"Error executing script with engine: {str(e)}")
                return False
        
        # Fall back to built-in eval for Python scripts if no engine
        logger.warning(f"No script engine found for {script_language}, using built-in eval for Python only")
        
        try:
            # Create a context with node data
            context = {
                "input": node_data.get("input", {}),
                "params": node_data.get("params", {}),
                "resources": node_data.get("resources", {})
            }
            
            # Execute the script
            if script_language == "python":
                # This is not secure! In a real system, use a sandbox
                result = eval(script, {"__builtins__": {}}, context)
                return bool(result)
            else:
                # For JavaScript and other languages, we just return False
                logger.warning(f"Execution of {script_language} scripts not implemented")
                return False
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return False
    
    def _resolve_value(self, value: Any, node_data: Dict[str, Any]) -> Any:
        """
        Resolve value, handling placeholders and special cases.
        
        Args:
            value: The value to resolve
            node_data: Node data for resolving placeholders
            
        Returns:
            Resolved value
        """
        if isinstance(value, str):
            # Check if it's a placeholder
            if value.startswith("{{") and value.endswith("}}"):
                placeholder = value[2:-2].strip()
                parts = placeholder.split(".")
                
                current = node_data
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
                
                return current
            
            # Resolve any other placeholders in the string
            return self.resolve_placeholders(value, node_data)
            
        return value
    
    def _apply_transformations(self, transformations: Dict[str, Any], node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transformations to the data.
        
        Args:
            transformations: Transformation definitions
            node_data: Node data to transform
            
        Returns:
            Transformed data
        """
        if not transformations:
            return node_data
        
        # Clone the node data
        transformed_data = json.loads(json.dumps(node_data))
        
        # Apply each transformation
        for key, value in transformations.items():
            # Resolve any placeholders in the value
            resolved_value = self._resolve_value(value, node_data)
            
            # Set the transformed value
            self._set_nested_value(transformed_data, key, resolved_value)
        
        return transformed_data
    
    def _set_nested_value(self, data: Dict[str, Any], key_path: str, value: Any) -> None:
        """
        Set a value in a nested dictionary.
        
        Args:
            data: Dictionary to update
            key_path: Path to the key, using dot notation
            value: Value to set
        """
        parts = key_path.split(".")
        current = data
        
        # Navigate to the parent
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value

# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("if", IfNode)
    logger.info("Successfully registered IfNode with registry")
except ImportError:
    logger.warning("Could not register IfNode with registry - module not found")
except Exception as e:
    logger.error(f"Error registering IfNode with registry: {str(e)}")
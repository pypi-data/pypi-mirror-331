#!/usr/bin/env python
"""
Advanced Node API Server with Import Patching

A lightweight server that provides API access to node information, schemas, and operations.
Includes advanced import patching to handle problematic imports in node files.
"""

import os
import sys
import json
import importlib.util
import inspect
import traceback
import types
import ast
import re
from typing import Dict, Any, List, Optional, Type, Union, Set, Callable
import logging
from contextlib import asynccontextmanager

# Use FastAPI for creating the API server
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Add the parent directory to sys.path if needed
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add the act_workflow/act path to sys.path if needed
act_dir = os.path.join(parent_dir, "act")
if os.path.exists(act_dir) and act_dir not in sys.path:
    sys.path.append(act_dir)

# Global caches
NODE_CLASSES = {}
NODE_INSTANCES = {}
PATCHED_MODULES = set()

# Save original import function and other builtins
original_import = __import__

# Custom JSONResponse for pretty formatting
class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=True,
            indent=2,
            separators=(", ", ": "),
        ).encode("utf-8")

# Define missing classes for injection
class EnhancedBaseNodeClasses:
    """
    Provides definitions for classes that might be missing in base_node.py
    but are required by other node files.
    """
    @staticmethod
    def create_missing_classes():
        """
        Create all potential missing classes that might be needed.
        """
        from enum import Enum
        from pydantic import BaseModel, Field

        # Enums
        class NodeResourceType(str, Enum):
            """Enum defining possible resource types that nodes can interact with."""
            DATABASE = "database"
            FILE = "file"
            API = "api"
            MEMORY = "memory"
            COMPUTE = "compute"
            USER = "user"
            SYSTEM = "system"
            CUSTOM = "custom"

        class NodeOperationType(str, Enum):
            """Enum defining possible operation types for nodes."""
            CREATE = "create"
            READ = "read"
            UPDATE = "update"
            DELETE = "delete"
            TRANSFORM = "transform"
            CONDITION = "condition"
            LOOP = "loop"
            CALL = "call"
            CUSTOM = "custom"

        # Models
        class NodeResource(BaseModel):
            """Defines a resource that a node can access or modify."""
            name: str
            type: Union[NodeResourceType, str]
            description: str
            required: bool = False
            default: Optional[Any] = None
            configuration_parameters: List[str] = Field(default_factory=list)

        class NodeOperation(BaseModel):
            """Defines an operation that a node can perform."""
            name: str
            type: Union[NodeOperationType, str]
            description: str
            required_resources: List[str] = Field(default_factory=list)
            required_parameters: List[str] = Field(default_factory=list)
            produces: Optional[Dict[str, Any]] = None

        # Exception classes
        class NodeExecutionError(Exception):
            """Raised when node execution fails."""
            pass

        return {
            'NodeResourceType': NodeResourceType,
            'NodeOperationType': NodeOperationType,
            'NodeResource': NodeResource,
            'NodeOperation': NodeOperation,
            'NodeExecutionError': NodeExecutionError
        }

# Advanced module manipulation
class ModuleDict(dict):
    """
    Special dictionary for module attributes that can dynamically 
    generate missing attributes on demand.
    """
    def __init__(self, module, missing_classes):
        self.module = module
        self.missing_classes = missing_classes
        # Initialize with all existing module attributes
        super().__init__({name: getattr(module, name) for name in dir(module) 
                        if not name.startswith('__')})
        
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            # If the key is a known missing class, inject it
            if key in self.missing_classes:
                logger.debug(f"Dynamically injecting missing class {key} into {self.module.__name__}")
                # Create the class and inject it into the module
                cls = self.missing_classes[key]
                setattr(self.module, key, cls)
                # Add it to our dictionary
                self[key] = cls
                return cls
            raise KeyError(key)

class ImportPatcher:
    """Advanced import patching system to handle problematic imports."""
    
    @staticmethod
    def fix_syntax_errors(source_code):
        """
        Attempt to fix simple syntax errors in the source code.
        This is a very basic implementation and can only fix a few types of errors.
        """
        # Fix missing colons after if statements
        fixed_code = re.sub(r'(if\s+[^:]+)(\s*)$', r'\1:\2', source_code, flags=re.MULTILINE)
        
        return fixed_code
    
    @staticmethod
    def create_module_from_file(full_path, module_name):
        """
        Create a module from a file path with syntax error fixing.
        """
        try:
            # Try to read the file
            with open(full_path, 'r') as file:
                source = file.read()
                
            # Try to fix syntax errors
            fixed_source = ImportPatcher.fix_syntax_errors(source)
            
            # Create a module spec
            spec = importlib.machinery.ModuleSpec(
                name=module_name,
                loader=None,
                origin=full_path
            )
            
            # Create a new module
            module = types.ModuleType(spec.name)
            module.__file__ = full_path
            module.__spec__ = spec
            
            # Add the module to sys.modules
            sys.modules[module_name] = module
            
            # Execute the fixed code in the module's namespace
            exec(compile(fixed_source, full_path, 'exec'), module.__dict__)
            
            return module
        except Exception as e:
            logger.error(f"Error creating module from file {full_path}: {e}")
            return None
    
    @staticmethod
    def patch_import(name, globals=None, locals=None, fromlist=(), level=0):
        """
        Advanced import patching function that handles various import patterns.
        """
        logger.debug(f"Patching import: {name}, fromlist={fromlist}, level={level}")
        
        # Special case for base_node imports to inject missing classes
        if name == 'base_node' and fromlist:
            try:
                # Try regular import first
                module = original_import(name, globals, locals, (), level)
                
                # See what classes we need to add
                missing_classes = EnhancedBaseNodeClasses.create_missing_classes()
                module_dict = ModuleDict(module, missing_classes)
                
                # Patch the module with a custom __getattr__
                def __getattr__(name):
                    if name in missing_classes:
                        logger.debug(f"Injecting missing class {name} via __getattr__")
                        cls = missing_classes[name]
                        setattr(module, name, cls)
                        return cls
                    raise AttributeError(f"module '{module.__name__}' has no attribute '{name}'")
                
                module.__getattr__ = __getattr__
                
                # Mark as patched
                PATCHED_MODULES.add(module.__name__)
                
                return module
            except ImportError:
                logger.warning(f"Failed to import base_node directly")
        
        # Handle relative imports with no parent package
        if level > 0:
            # Get the potential module name from the fromlist
            if name == '' and fromlist:
                # Handle 'from . import x'
                for item in fromlist:
                    if item == 'base_node':
                        return original_import('base_node', globals, locals, (), 0)
            elif name.startswith('.'):
                # Handle 'from .x import y'
                abs_name = name[1:] if name.startswith('.') else name
                if abs_name == 'base_node':
                    return original_import('base_node', globals, locals, fromlist, 0)
        
        # Handle absolute imports from act package
        if name == 'act' or name.startswith('act.'):
            if name == 'act.base_node':
                # Map to local base_node
                logger.debug("Mapping act.base_node to base_node")
                return original_import('base_node', globals, locals, fromlist, 0)
            elif name == 'act.nodes.base_node':
                logger.debug("Mapping act.nodes.base_node to base_node")
                return original_import('base_node', globals, locals, fromlist, 0)
            elif name == 'act':
                # Create a fake act module as a package
                logger.debug("Creating fake act package")
                if 'act' not in sys.modules:
                    act_module = types.ModuleType('act')
                    act_module.__path__ = []  # Make it a package
                    sys.modules['act'] = act_module
                return sys.modules['act']
        
        # Try the original import
        try:
            return original_import(name, globals, locals, fromlist, level)
        except ImportError as e:
            logger.debug(f"Original import failed: {e}")
            
            # Last resort - try to create the module directly from a file
            if level == 0 and '.' not in name:
                potential_file = os.path.join(current_dir, f"{name}.py")
                if os.path.exists(potential_file):
                    logger.debug(f"Attempting to create module directly from {potential_file}")
                    module = ImportPatcher.create_module_from_file(potential_file, name)
                    if module:
                        return module
            
            # Reraise the original exception
            raise

def patch_sys_modules():
    """
    Patch existing modules in sys.modules to inject missing classes.
    """
    if 'base_node' in sys.modules and 'base_node' not in PATCHED_MODULES:
        module = sys.modules['base_node']
        missing_classes = EnhancedBaseNodeClasses.create_missing_classes()
        
        # Add missing classes to the module
        for name, cls in missing_classes.items():
            if not hasattr(module, name):
                logger.debug(f"Injecting missing class {name} into base_node module")
                setattr(module, name, cls)
        
        # Mark as patched
        PATCHED_MODULES.add('base_node')

def discover_all_nodes() -> Dict[str, Type]:
    """
    Aggressively discover all node classes in the current directory.
    """
    node_classes = {}
    
    logger.info("Starting aggressive node discovery process")
    
    # Install our import patcher
    original_sys_import = __builtins__['__import__']
    __builtins__['__import__'] = ImportPatcher.patch_import
    
    try:
        # Find all potential node files
        node_files = []
        for filename in os.listdir(current_dir):
            if filename.endswith('.py') and not filename.startswith('__') and filename != os.path.basename(__file__):
                if 'Node' in filename or 'node' in filename:  # More likely to be a node file
                    node_files.insert(0, filename)  # Prioritize
                else:
                    node_files.append(filename)
                logger.info(f"Found potential node file: {filename}")
        
        # Process base_node.py first if it exists
        if 'base_node.py' in node_files:
            node_files.remove('base_node.py')
            node_files.insert(0, 'base_node.py')
        
        # Process each file
        for filename in node_files:
            module_name = os.path.splitext(filename)[0]
            logger.info(f"Processing file: {filename}")
            
            try:
                # Try to import the module
                if module_name in sys.modules:
                    module = sys.modules[module_name]
                    logger.info(f"Module {module_name} already imported")
                else:
                    logger.info(f"Importing module {module_name}")
                    # Patch existing modules first
                    patch_sys_modules()
                    # Import the module
                    module = importlib.import_module(module_name)
                
                # Look for node classes
                for item_name, item in inspect.getmembers(module, inspect.isclass):
                    # Skip if it doesn't look like a node class
                    if not (item_name.endswith('Node') or 'Node' in item_name):
                        continue
                    
                    logger.info(f"Found potential node class: {item_name}")
                    
                    # Skip if it's BaseNode itself
                    if item_name == 'BaseNode':
                        continue
                    
                    try:
                        # Try to instantiate it
                        instance = item()
                        
                        # Check if it has get_schema method
                        if hasattr(instance, 'get_schema'):
                            try:
                                schema = instance.get_schema()
                                
                                # Try to get node_type
                                node_type = None
                                if hasattr(schema, 'node_type'):
                                    node_type = schema.node_type
                                elif hasattr(schema, 'get'):
                                    node_type = schema.get('node_type')
                                
                                # Fall back to class name if no node_type
                                if not node_type:
                                    node_type = item_name[:-4].lower() if item_name.endswith('Node') else item_name.lower()
                                
                                # Register the node class
                                node_classes[node_type] = item
                                logger.info(f"Successfully registered node type '{node_type}' from class {item_name}")
                            except Exception as e:
                                logger.error(f"Error getting schema from {item_name}: {e}")
                                # Still try to register based on class name
                                node_type = item_name[:-4].lower() if item_name.endswith('Node') else item_name.lower()
                                node_classes[node_type] = item
                                logger.info(f"Registered node type '{node_type}' based on class name {item_name} (schema error)")
                        else:
                            logger.warning(f"Class {item_name} doesn't have get_schema method")
                    except Exception as e:
                        logger.error(f"Error instantiating {item_name}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                logger.error(traceback.format_exc())
                
    finally:
        # Restore original import
        __builtins__['__import__'] = original_sys_import
    
    return node_classes

def get_node_instance(node_type: str) -> Any:
    """
    Get a node instance by type, creating it if needed.
    """
    if node_type not in NODE_INSTANCES:
        if node_type not in NODE_CLASSES:
            raise ValueError(f"Unknown node type: {node_type}")
        
        try:
            NODE_INSTANCES[node_type] = NODE_CLASSES[node_type]()
            logger.info(f"Created instance for node type: {node_type}")
        except Exception as e:
            logger.error(f"Error creating instance for node type {node_type}: {e}")
            raise
    
    return NODE_INSTANCES[node_type]

def get_schema_dict(node_instance) -> Dict[str, Any]:
    """
    Get a schema dictionary from a node instance.
    """
    try:
        schema = node_instance.get_schema()
        
        # Convert to dictionary (handling both Pydantic v1 and v2)
        if hasattr(schema, 'model_dump'):  # Pydantic v2
            return schema.model_dump()
        elif hasattr(schema, 'dict'):  # Pydantic v1
            return schema.dict()
        else:
            # Fall back to manual conversion
            result = {}
            for key, value in vars(schema).items():
                if not key.startswith('_'):
                    result[key] = value
            return result
    except Exception as e:
        logger.error(f"Error getting schema dictionary: {e}")
        return {"error": str(e)}

def format_schema(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the schema dictionary for better readability.
    """
    try:
        # Group by category
        result = {
            "metadata": {
                "node_type": schema_dict.get("node_type"),
                "version": schema_dict.get("version", ""),
                "description": schema_dict.get("description", ""),
                "tags": schema_dict.get("tags", []),
                "author": schema_dict.get("author", "")
            },
            "parameters": {},
            "resources": {},
            "operations": {},
            "outputs": schema_dict.get("outputs", {})
        }
        
        # Format parameters
        parameters = schema_dict.get("parameters", [])
        if parameters:
            if isinstance(parameters, list):
                for param in parameters:
                    param_dict = param
                    if not isinstance(param, dict):
                        # Convert to dict if it's an object
                        if hasattr(param, 'model_dump'):
                            param_dict = param.model_dump()
                        elif hasattr(param, 'dict'):
                            param_dict = param.dict()
                        else:
                            param_dict = {k: v for k, v in vars(param).items() if not k.startswith('_')}
                    
                    name = param_dict.get("name", "unknown")
                    result["parameters"][name] = {
                        "type": param_dict.get("type", "unknown"),
                        "description": param_dict.get("description", ""),
                        "required": param_dict.get("required", True),
                        "default": param_dict.get("default")
                    }
                    
                    # Add enum if present
                    if "enum" in param_dict and param_dict["enum"]:
                        result["parameters"][name]["enum"] = param_dict["enum"]
        
        # Format resources
        resources = schema_dict.get("resources", [])
        if resources:
            if isinstance(resources, list):
                for resource in resources:
                    resource_dict = resource
                    if not isinstance(resource, dict):
                        # Convert to dict if it's an object
                        if hasattr(resource, 'model_dump'):
                            resource_dict = resource.model_dump()
                        elif hasattr(resource, 'dict'):
                            resource_dict = resource.dict()
                        else:
                            resource_dict = {k: v for k, v in vars(resource).items() if not k.startswith('_')}
                    
                    name = resource_dict.get("name", "unknown")
                    result["resources"][name] = {
                        "type": resource_dict.get("type", "unknown"),
                        "description": resource_dict.get("description", ""),
                        "required": resource_dict.get("required", False),
                        "default": resource_dict.get("default"),
                        "configuration_parameters": resource_dict.get("configuration_parameters", [])
                    }
        
        # Format operations
        operations = schema_dict.get("operations", [])
        if operations:
            if isinstance(operations, list):
                for operation in operations:
                    operation_dict = operation
                    if not isinstance(operation, dict):
                        # Convert to dict if it's an object
                        if hasattr(operation, 'model_dump'):
                            operation_dict = operation.model_dump()
                        elif hasattr(operation, 'dict'):
                            operation_dict = operation.dict()
                        else:
                            operation_dict = {k: v for k, v in vars(operation).items() if not k.startswith('_')}
                    
                    name = operation_dict.get("name", "unknown")
                    result["operations"][name] = {
                        "type": operation_dict.get("type", "unknown"),
                        "description": operation_dict.get("description", ""),
                        "required_resources": operation_dict.get("required_resources", []),
                        "required_parameters": operation_dict.get("required_parameters", []),
                        "produces": operation_dict.get("produces", {})
                    }
        
        return result
    except Exception as e:
        logger.error(f"Error formatting schema: {e}")
        return {"error": str(e), "original_schema": schema_dict}

def extract_parameters_from_schema(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract parameters from a node schema.
    """
    parameters = {}
    
    # Extract parameters
    schema_params = schema_dict.get("parameters", [])
    if schema_params:
        if isinstance(schema_params, list):
            for param in schema_params:
                param_dict = param
                if not isinstance(param, dict):
                    # Convert to dict if it's an object
                    if hasattr(param, 'model_dump'):
                        param_dict = param.model_dump()
                    elif hasattr(param, 'dict'):
                        param_dict = param.dict()
                    else:
                        param_dict = {k: v for k, v in vars(param).items() if not k.startswith('_')}
                
                name = param_dict.get("name", "unknown")
                parameters[name] = {
                    "type": param_dict.get("type", "unknown"),
                    "description": param_dict.get("description", ""),
                    "required": param_dict.get("required", True),
                    "default": param_dict.get("default")
                }
                
                # Add enum if present
                if "enum" in param_dict and param_dict["enum"]:
                    parameters[name]["enum"] = param_dict["enum"]
    
    return parameters

def extract_operations_from_schema(schema_dict: Dict[str, Any], node_instance) -> Dict[str, Any]:
    """
    Extract operations from a node schema with parameter information.
    """
    operations = {}
    all_parameters = extract_parameters_from_schema(schema_dict)
    
    # Extract operations
    schema_ops = schema_dict.get("operations", [])
    
    # For nodes like SlackNode that use enum constants for operations
    operation_param = None
    for param in schema_dict.get("parameters", []):
        param_dict = param
        if not isinstance(param, dict):
            if hasattr(param, 'model_dump'):
                param_dict = param.model_dump()
            elif hasattr(param, 'dict'):
                param_dict = param.dict()
            else:
                param_dict = {k: v for k, v in vars(param).items() if not k.startswith('_')}
        
        if param_dict.get("name") == "operation" and "enum" in param_dict:
            operation_param = param_dict
            break
    
    # If we found an operation parameter with enum values
    if operation_param:
        # Try to find validate_custom method to analyze which params are needed for each operation
        validate_custom_source = None
        if hasattr(node_instance, 'validate_custom'):
            validate_custom_source = inspect.getsource(node_instance.validate_custom)
        
        for op_name in operation_param.get("enum", []):
            # Check if method exists for this operation
            method_name = f"_operation_{op_name.lower()}"
            alt_method_name = f"operation_{op_name.lower()}"
            
            # Get method source if available to analyze parameter usage
            method_source = None
            if hasattr(node_instance, method_name):
                method = getattr(node_instance, method_name)
                try:
                    method_source = inspect.getsource(method)
                except Exception:
                    pass
            elif hasattr(node_instance, alt_method_name):
                method = getattr(node_instance, alt_method_name)
                try:
                    method_source = inspect.getsource(method)
                except Exception:
                    pass
            
            # Extract relevant parameters for this operation
            op_parameters = {}
            
            # Always include operation parameter
            if "operation" in all_parameters:
                op_parameters["operation"] = all_parameters["operation"]
            
            # Always include authentication/common parameters
            common_params = ["token", "api_key", "org_id"]
            for param in common_params:
                if param in all_parameters:
                    op_parameters[param] = all_parameters[param]
            
            # Use source code analysis to find required parameters
            if method_source:
                # Check which parameters from all_parameters are mentioned in the method source
                for param_name, param_info in all_parameters.items():
                    if param_name != "operation" and param_name not in common_params:
                        param_var = f'params.get("{param_name}"'
                        if param_var in method_source:
                            op_parameters[param_name] = param_info
            
            # If we have validate_custom_source, use it to determine required parameters
            if validate_custom_source:
                # Look for conditional blocks for this operation
                operation_block = None
                lines = validate_custom_source.split('\n')
                in_operation_block = False
                operation_block_lines = []
                
                for line in lines:
                    if f'operation == {op_name}' in line or f'operation == "{op_name}"' in line or f"operation == '{op_name}'" in line:
                        in_operation_block = True
                    elif in_operation_block and ('elif' in line or 'else' in line):
                        in_operation_block = False
                    
                    if in_operation_block:
                        operation_block_lines.append(line)
                
                operation_block = '\n'.join(operation_block_lines)
                
                # If we found a validation block, extract mentioned parameters
                if operation_block:
                    for param_name in all_parameters:
                        if param_name != "operation" and param_name not in op_parameters:
                            if f'params.get("{param_name}")' in operation_block:
                                op_parameters[param_name] = all_parameters[param_name]
            
            # Default operation details
            operations[op_name] = {
                "name": op_name,
                "description": f"Operation {op_name}",
                "implemented": hasattr(node_instance, method_name) or hasattr(node_instance, alt_method_name),
                "parameters": op_parameters
            }
            
            # Try to get docstring from method
            if hasattr(node_instance, method_name) and getattr(node_instance, method_name).__doc__:
                operations[op_name]["documentation"] = getattr(node_instance, method_name).__doc__.strip()
            elif hasattr(node_instance, alt_method_name) and getattr(node_instance, alt_method_name).__doc__:
                operations[op_name]["documentation"] = getattr(node_instance, alt_method_name).__doc__.strip()
    
    # Process standard operations list
    if schema_ops:
        if isinstance(schema_ops, list):
            for operation in schema_ops:
                op_dict = operation
                if not isinstance(operation, dict):
                    # Convert to dict if it's an object
                    if hasattr(operation, 'model_dump'):
                        op_dict = operation.model_dump()
                    elif hasattr(operation, 'dict'):
                        op_dict = operation.dict()
                    else:
                        op_dict = {k: v for k, v in vars(operation).items() if not k.startswith('_')}
                
                name = op_dict.get("name", "unknown")
                required_params = op_dict.get("required_parameters", [])
                
                # Filter parameters to only include those required by this operation
                op_parameters = {}
                for param_name, param_info in all_parameters.items():
                    if param_name in required_params:
                        op_parameters[param_name] = param_info
                
                operations[name] = {
                    "name": name,
                    "type": op_dict.get("type", "unknown"),
                    "description": op_dict.get("description", ""),
                    "required_resources": op_dict.get("required_resources", []),
                    "required_parameters": op_dict.get("required_parameters", []),
                    "produces": op_dict.get("produces", {}),
                    "parameters": op_parameters
                }
                
                # Check if the operation is implemented
                method_name = f"operation_{name}"
                if hasattr(node_instance, method_name):
                    operations[name]["implemented"] = True
                    
                    # Get the method's docstring if available
                    method = getattr(node_instance, method_name)
                    if method.__doc__:
                        operations[name]["documentation"] = method.__doc__.strip()
                else:
                    operations[name]["implemented"] = False
    
    # No operations found in the schema, try to discover them from methods
    if not operations:
        for method_name in dir(node_instance):
            if method_name.startswith("operation_") or method_name.startswith("_operation_"):
                op_name = method_name.replace("operation_", "").replace("_operation_", "")
                method = getattr(node_instance, method_name)
                
                # Extract parameters used in this method
                op_parameters = {}
                try:
                    method_source = inspect.getsource(method)
                    for param_name, param_info in all_parameters.items():
                        param_var = f'params.get("{param_name}"'
                        if param_var in method_source:
                            op_parameters[param_name] = param_info
                except Exception:
                    # If we can't get the source, include all parameters
                    op_parameters = all_parameters
                
                operations[op_name] = {
                    "name": op_name,
                    "implemented": True,
                    "description": method.__doc__.strip() if method.__doc__ else f"Operation {op_name}",
                    "parameters": op_parameters
                }
    
    return operations

# Define lifespan for application startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    global NODE_CLASSES
    logger.info("Starting Node API Server")
    logger.info(f"Current directory: {current_dir}")
    
    # Discover node classes
    NODE_CLASSES = discover_all_nodes()
    logger.info(f"Discovered {len(NODE_CLASSES)} node types: {', '.join(NODE_CLASSES.keys())}")
    
    yield
    
    # Shutdown code
    logger.info("Shutting down Node API Server")
    global NODE_INSTANCES
    NODE_INSTANCES.clear()

# Create the FastAPI app
app = FastAPI(
    title="Node API",
    description="API for accessing node information, schemas, and operations",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=PrettyJSONResponse  # Use pretty JSON by default
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Node API Server",
        "version": "1.0.0",
        "description": "API for accessing node information, schemas, and operations",
        "endpoints": {
            "GET /nodes": "List all available node types",
            "GET /nodes/all": "Get all nodes with their operations and parameters",
            "GET /nodes/{node_type}": "Get information about a specific node type",
            "GET /nodes/{node_type}/schema": "Get the schema for a specific node type",
            "GET /nodes/{node_type}/operations": "Get available operations for a node type",
            "GET /nodes/{node_type}/operations/{operation_name}": "Get detailed information about a specific operation",
            "POST /nodes/{node_type}/execute": "Execute a node with provided data",
            "POST /nodes/{node_type}/operations/{operation_name}": "Execute a specific operation of a node",
            "POST /reload": "Force reload of all nodes"
        }
    }

@app.get("/nodes")
async def list_nodes(format: str = Query("simple", description="Response format (simple, detailed)")):
    """List all available node types."""
    try:
        if format == "simple":
            return {"node_types": list(NODE_CLASSES.keys())}
        else:
            result = {}
            for node_type, node_class in NODE_CLASSES.items():
                try:
                    instance = get_node_instance(node_type)
                    schema = get_schema_dict(instance)
                    result[node_type] = {
                        "description": schema.get("description", ""),
                        "version": schema.get("version", ""),
                        "tags": schema.get("tags", [])
                    }
                except Exception as e:
                    result[node_type] = {"error": str(e)}
            return result
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing nodes: {str(e)}")

@app.get("/nodes/all")
async def get_all_nodes_with_operations_and_parameters():
    """Get all nodes with their operations and parameters in a single JSON."""
    try:
        result = {}
        
        for node_type, node_class in NODE_CLASSES.items():
            try:
                # Get node instance
                instance = get_node_instance(node_type)
                
                # Get schema
                schema_dict = get_schema_dict(instance)
                
                # Extract operations and parameters
                parameters = extract_parameters_from_schema(schema_dict)
                operations = extract_operations_from_schema(schema_dict, instance)
                
                # Create node info
                node_info = {
                    "node_type": node_type,
                    "class_name": node_class.__name__,
                    "version": schema_dict.get("version", ""),
                    "description": schema_dict.get("description", ""),
                    "tags": schema_dict.get("tags", []),
                    "author": schema_dict.get("author", ""),
                    "parameters": parameters,
                    "operations": operations,
                    "outputs": schema_dict.get("outputs", {})
                }
                
                result[node_type] = node_info
                
            except Exception as e:
                logger.error(f"Error processing node {node_type}: {e}")
                result[node_type] = {"error": str(e)}
        
        return result
    except Exception as e:
        logger.error(f"Error getting all nodes data: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting all nodes data: {str(e)}")

@app.get("/nodes/{node_type}")
async def get_node_info(node_type: str):
    """Get information about a specific node type."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        instance = get_node_instance(node_type)
        schema = get_schema_dict(instance)
        
        # Basic node information
        node_info = {
            "node_type": node_type,
            "class_name": NODE_CLASSES[node_type].__name__,
            "version": schema.get("version", ""),
            "description": schema.get("description", ""),
            "tags": schema.get("tags", []),
            "author": schema.get("author"),
            "parameters_count": len(schema.get("parameters", [])),
            "resources_count": len(schema.get("resources", [])),
            "operations_count": len(schema.get("operations", [])),
            "outputs": schema.get("outputs", {})
        }
        
        return node_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting node info for {node_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting node info: {str(e)}")

@app.get("/nodes/{node_type}/schema")
async def get_node_schema(
    node_type: str, 
    format: str = Query("raw", description="Schema format (raw, formatted)")
):
    """Get the schema for a specific node type."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        instance = get_node_instance(node_type)
        schema_dict = get_schema_dict(instance)
        
        if format == "formatted":
            return format_schema(schema_dict)
        else:
            return schema_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting schema for {node_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting schema: {str(e)}")

@app.get("/nodes/{node_type}/operations")
async def get_node_operations(node_type: str):
    """Get available operations for a node type."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        instance = get_node_instance(node_type)
        schema_dict = get_schema_dict(instance)
        
        # Use the comprehensive extraction function that also checks for enum-based operations
        operations = extract_operations_from_schema(schema_dict, instance)
        
        return operations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting operations for {node_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting operations: {str(e)}")
@app.get("/nodes/{node_type}/operations/{operation_name}")
async def get_operation_detail(node_type: str, operation_name: str):
    """Get detailed information about a specific node operation."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        instance = get_node_instance(node_type)
        schema_dict = get_schema_dict(instance)
        
        # Get all operations using our comprehensive extraction function
        all_operations = extract_operations_from_schema(schema_dict, instance)
        
        # Check if requested operation exists
        if operation_name not in all_operations:
            raise HTTPException(status_code=404, detail=f"Operation '{operation_name}' not found for node type '{node_type}'")
        
        # Return the operation details
        operation = all_operations[operation_name]
        
        # Add implementation check if not already present
        if "implemented" not in operation:
            method_name = f"operation_{operation_name}"
            alt_method_name = f"_operation_{operation_name}"
            operation["implemented"] = (
                hasattr(instance, method_name) or 
                hasattr(instance, alt_method_name)
            )
            
            # Get docstring if available
            if hasattr(instance, method_name) and getattr(instance, method_name).__doc__:
                operation["documentation"] = getattr(instance, method_name).__doc__.strip()
            elif hasattr(instance, alt_method_name) and getattr(instance, alt_method_name).__doc__:
                operation["documentation"] = getattr(instance, alt_method_name).__doc__.strip()
                
        return operation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting operation detail for {node_type}/{operation_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting operation detail: {str(e)}")
@app.post("/nodes/{node_type}/execute")
async def execute_node(node_type: str, request: Request):
    """Execute a node with provided data."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        # Get the request body as JSON
        try:
            node_data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        
        # Get node instance
        instance = get_node_instance(node_type)
        
        # Execute the node with patched imports
        original_sys_import = __builtins__['__import__']
        __builtins__['__import__'] = ImportPatcher.patch_import
        
        try:
            # Execute the node
            if hasattr(instance, 'execute_sync'):
                result = instance.execute_sync(node_data)
            elif hasattr(instance, 'execute'):
                # For async execution, create a new event loop
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(instance.execute(node_data))
                finally:
                    loop.close()
            else:
                raise HTTPException(status_code=500, detail=f"Node {node_type} has no execute method")
                
            return result
        finally:
            # Restore original import
            __builtins__['__import__'] = original_sys_import
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing node {node_type}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error executing node: {str(e)}")

@app.post("/nodes/{node_type}/operations/{operation_name}")
async def execute_operation(node_type: str, operation_name: str, request: Request):
    """Execute a specific operation of a node."""
    try:
        if node_type not in NODE_CLASSES:
            raise HTTPException(status_code=404, detail=f"Node type '{node_type}' not found")
        
        # Get the request body as JSON
        try:
            node_data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        
        # Get node instance
        instance = get_node_instance(node_type)
        
        # Check if the operation exists
        operation_method_name = f"operation_{operation_name}"
        if not hasattr(instance, operation_method_name):
            # Check for alternate naming
            operation_method_name = operation_name
            if not hasattr(instance, operation_method_name):
                raise HTTPException(status_code=404, detail=f"Operation '{operation_name}' not found")
        
        # Execute the operation with patched imports
        original_sys_import = __builtins__['__import__']
        __builtins__['__import__'] = ImportPatcher.patch_import
        
        try:
            # Execute the operation
            operation_method = getattr(instance, operation_method_name)
            
            # Check if it's async
            if inspect.iscoroutinefunction(operation_method):
                # For async execution, create a new event loop
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(operation_method(node_data))
                finally:
                    loop.close()
            else:
                result = operation_method(node_data)
                
            return result
        finally:
            # Restore original import
            __builtins__['__import__'] = original_sys_import
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing operation {operation_name} on node {node_type}: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error executing operation: {str(e)}")

# Force node reload endpoint
@app.post("/reload")
async def reload_nodes():
    """Force reload of all nodes."""
    try:
        global NODE_CLASSES, NODE_INSTANCES, PATCHED_MODULES
        
        # Clear caches
        NODE_INSTANCES.clear()
        PATCHED_MODULES.clear()
        
        # Clear modules from sys.modules
        modules_to_remove = []
        for module_name in sys.modules:
            if (module_name.endswith('Node') or 
                module_name == 'base_node' or 
                'node' in module_name.lower()):
                modules_to_remove.append(module_name)
        
        # Remove them (can't modify dict during iteration)
        for module_name in modules_to_remove:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        # Discover nodes again
        NODE_CLASSES = discover_all_nodes()
        
        return {
            "success": True,
            "node_types": list(NODE_CLASSES.keys())
        }
    except Exception as e:
        logger.error(f"Error reloading nodes: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error reloading nodes: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

def main():
    """Run the server."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Node API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        # Enable more verbose logging for uvicorn
        uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        uvicorn_log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    # Use the actual filename in the module string
    module_name = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(
        f"{module_name}:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )

if __name__ == "__main__":
    main()
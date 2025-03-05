import importlib
import traceback
import logging
import json
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta
import re
import os
from pathlib import Path
import inspect
import sys

from colorama import init, Fore, Style
from tabulate import tabulate

from .actfile_parser import ActfileParser, ActfileParserError
from .workflow_engine import WorkflowEngine
from .node_context import NodeContext

# Initialize colorama for cross-platform color support
init()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExecutionManager:
    def __init__(self, actfile_path: str = 'Actfile', sandbox_timeout: int = 600):
        logger.info(f"Initializing ExecutionManager")
        self.actfile_path = actfile_path
        self.node_results = {}
        self.execution_queue = asyncio.Queue()
        self.sandbox_timeout = sandbox_timeout
        self.sandbox_start_time = None
        self.actfile_path = Path(actfile_path)
        self.workflow_engine = WorkflowEngine()
        self.node_loading_status = {}
        self.load_workflow()

    def load_workflow(self):
        logger.info("Loading workflow data")
        try:
            parser = ActfileParser(self.actfile_path)
            self.workflow_data = parser.parse()
            self.actfile_parser = parser
        except ActfileParserError as e:
            logger.error(f"Error parsing Actfile: {e}")
            raise

        self.load_node_executors()

    def discover_node_classes(self):
        """
        Discover all node classes in the nodes directory.
        Returns a dictionary of node types mapping to their class objects.
        """
        node_classes = {}
        
        # Import the nodes package to get its directory
        from . import nodes
        nodes_dir = Path(nodes.__file__).parent
        logger.info(f"Scanning nodes directory: {nodes_dir}")
        
        # Dictionary to track node files and their potential node classes
        node_files = {}
        
        # First, check if a node registry exists
        try:
            # Try to load the node registry
            from .nodes.node_registry import NODES
            logger.info(f"Found node registry with {len(NODES)} nodes")
            node_classes.update(NODES)
        except (ImportError, AttributeError) as e:
            logger.debug(f"No node registry found or error loading it: {e}")
        
        # Scan all Python files in the nodes directory
        for file_path in nodes_dir.glob('*.py'):
            if file_path.name.startswith('__'):  # Skip __init__.py and similar
                continue
                
            module_name = file_path.stem
            if module_name == 'base_node' or module_name == 'node_registry':
                continue  # Skip base node and registry
            
            logger.debug(f"Found node file: {module_name}")
            
            # Track this file for later importing
            node_files[module_name] = file_path
        
        # Log all found node files
        logger.info(f"Found {len(node_files)} potential node files: {', '.join(node_files.keys())}")
        
        # Process each node file
        for module_name, file_path in node_files.items():
            try:
                # Import the module
                logger.debug(f"Importing module: {module_name}")
                module = importlib.import_module(f".nodes.{module_name}", package="act")
                
                # Find classes in the module
                for attr_name in dir(module):
                    if attr_name.startswith('__'):  # Skip private attributes
                        continue
                        
                    attr = getattr(module, attr_name)
                    if not inspect.isclass(attr):  # Skip if not a class
                        continue
                        
                    # Check if this looks like a node class
                    # 1. Name ends with "Node"
                    # 2. Has execute method
                    # 3. Name matches module name with Node suffix
                    if (attr_name.endswith('Node') or 
                        (hasattr(attr, 'execute') and callable(getattr(attr, 'execute'))) or
                        attr_name.lower() == module_name.lower() or
                        attr_name.lower() == f"{module_name.lower()}node"):
                        
                        # Extract node type from class name or module name
                        node_type = None
                        
                        # Try getting node_type from get_schema if it exists
                        if hasattr(attr, 'get_schema') and callable(getattr(attr, 'get_schema')):
                            try:
                                obj = attr()
                                schema = obj.get_schema()
                                if hasattr(schema, 'node_type'):
                                    node_type = schema.node_type
                                elif isinstance(schema, dict) and 'node_type' in schema:
                                    node_type = schema['node_type']
                            except Exception as e:
                                logger.debug(f"Error getting schema from {attr_name}: {e}")
                        
                        # If no node_type from schema, derive from class name
                        if not node_type:
                            if attr_name.endswith('Node'):
                                node_type = attr_name[:-4]  # Remove 'Node' suffix
                            else:
                                node_type = attr_name
                        
                        # Multiple class names could map to same node type
                        # To handle case sensitivity, normalize to original case format from workflow 
                        for workflow_node_type in self.workflow_data.get('nodes', {}).values():
                            if workflow_node_type.get('type', '').lower() == node_type.lower():
                                node_type = workflow_node_type.get('type')
                                break
                                
                        logger.info(f"Found node class {attr_name} in {module_name}, registering as {node_type}")
                        node_classes[node_type] = attr
            
            except Exception as e:
                logger.error(f"Error processing node file {module_name}: {e}")
                logger.error(traceback.format_exc())
        
        return node_classes

    def load_node_executors(self):
        """
        Dynamically loads node executors based on node types in workflow_data.
        Uses advanced node discovery to find all available node types.
        """
        logger.info("Loading node executors")
        node_types_in_workflow = set(node['type'] for node in self.workflow_data['nodes'].values())
        self.node_executors = {}
        self.node_loading_status = {node_type: {'status': 'pending', 'message': ''} for node_type in node_types_in_workflow}
        
        # Discover all node classes
        all_node_classes = self.discover_node_classes()
        logger.info(f"Discovered {len(all_node_classes)} node types: {', '.join(all_node_classes.keys())}")
        
        # Process each node type needed for this workflow
        for node_type in node_types_in_workflow:
            try:
                logger.info(f"Attempting to load node type: {node_type}")
                node_instance = None
                
                # Check if we have this node type in our discovered classes
                if node_type in all_node_classes:
                    node_class = all_node_classes[node_type]
                    node_instance = self._instantiate_node(node_class)
                    self.node_loading_status[node_type] = {
                        'status': 'success', 
                        'message': f'Loaded from discovered class {node_class.__name__}'
                    }
                # Try case-insensitive match
                elif any(nt.lower() == node_type.lower() for nt in all_node_classes.keys()):
                    matching_type = next(nt for nt in all_node_classes.keys() if nt.lower() == node_type.lower())
                    node_class = all_node_classes[matching_type]
                    node_instance = self._instantiate_node(node_class)
                    self.node_loading_status[node_type] = {
                        'status': 'success', 
                        'message': f'Loaded using case-insensitive match from {node_class.__name__}'
                    }
                else:
                    # Not found in discovered classes
                    raise ImportError(f"Could not find suitable node class for {node_type}")
                
                if node_instance:
                    self.node_executors[node_type] = node_instance
                    logger.info(f"Successfully loaded node executor for {node_type}")
                else:
                    raise ImportError(f"Could not instantiate node class for {node_type}")

            except Exception as e:
                logger.error(f"Error loading node type '{node_type}': {str(e)}")
                logger.error(traceback.format_exc())
                
                # Fall back to GenericNode
                try:
                    from .nodes.GenericNode import GenericNode
                    self.node_executors[node_type] = GenericNode()
                    self.node_loading_status[node_type] = {
                        'status': 'fallback',
                        'message': f'Fallback to GenericNode: {str(e)}'
                    }
                    logger.info(f"Fallback to GenericNode for {node_type}")
                except ImportError:
                    logger.error("Could not import GenericNode for fallback!")
                    self.node_loading_status[node_type] = {
                        'status': 'error',
                        'message': f'Failed to load node: {str(e)}'
                    }

        # Print node loading status table
        self._print_node_loading_status()

    def _print_node_loading_status(self):
        """Print a formatted table showing the loading status of all nodes"""
        headers = ["Node Type", "Status", "Message"]
        table_data = []
        
        for node_type, status in self.node_loading_status.items():
            status_symbol = "🟢" if status['status'] == 'success' else "🔴" if status['status'] == 'fallback' else "⚪"
            status_color = (Fore.GREEN if status['status'] == 'success' else 
                            Fore.RED if status['status'] == 'fallback' else 
                            Fore.YELLOW)
            
            table_data.append([
                node_type,
                f"{status_color}{status_symbol} {status['status'].upper()}{Style.RESET_ALL}",
                status['message']
            ])

        table = tabulate(table_data, headers=headers, tablefmt="grid")
        print("\nNode Loading Status:")
        print(table)
        print()  # Add a blank line after the table

    def _instantiate_node(self, node_class):
        """Helper method to instantiate a node with proper parameters"""
        if hasattr(node_class.__init__, '__code__') and 'sandbox_timeout' in node_class.__init__.__code__.co_varnames:
            node_instance = node_class(sandbox_timeout=self.sandbox_timeout)
        else:
            node_instance = node_class()
            
        if hasattr(node_instance, 'set_execution_manager'):
            node_instance.set_execution_manager(self)
            
        return node_instance

    def _snake_case(self, name):
        """Convert string to snake_case"""
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def _pascal_case(self, name):
        """Convert string to PascalCase"""
        return ''.join(word.capitalize() for word in re.split(r'[_\s]+', name))

    def execute_workflow(self) -> Dict[str, Any]:
        """Execute the workflow with async support"""
        # Use asyncio to run the async version of execute_workflow
        return asyncio.run(self.execute_workflow_async())

    async def execute_workflow_async(self) -> Dict[str, Any]:
        """Async version of execute_workflow"""
        logger.info(f"Starting execution of workflow")
        self.node_results = {}
        execution_queue = []
        self.sandbox_start_time = datetime.now()

        try:
            start_node_name = self.actfile_parser.get_start_node()
            if not start_node_name:
                logger.error("No start node specified in Actfile.")
                return {"status": "error", "message": "No start node specified in Actfile.", "results": {}}

            execution_queue.append((start_node_name, None))

            while execution_queue:
                

                node_name, input_data = execution_queue.pop(0)
                node_result = await self.execute_node_async(node_name, input_data)
                self.node_results[node_name] = node_result

                if node_result.get('status') == 'error':
                    logger.error(f"Node {node_name} execution failed. Stopping workflow.")
                    # Print node execution results so far
                    self._print_node_execution_results()
                    return {
                        "status": "error",
                        "message": f"Workflow execution failed at node {node_name}",
                        "results": self.node_results
                    }

                successors = self.actfile_parser.get_node_successors(node_name)
                for successor in successors:
                    logger.debug(f"Queueing next node: {successor}")
                    execution_queue.append((successor, node_result))

            logger.info("Workflow execution completed")
            # Print node execution results
            self._print_node_execution_results()

            return {
                "status": "success",
                "message": "Workflow executed successfully",
                "results": self.node_results
            }

        except Exception as e:
            logger.error(f"Error during workflow execution: {str(e)}", exc_info=True)
            # Print node execution results so far
            self._print_node_execution_results()
            return {
                "status": "error",
                "message": f"Workflow execution failed: {str(e)}",
                "results": self.node_results
            }

    def execute_node(self, node_name: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a node with async support"""
        # Use asyncio to run the async version of execute_node
        return asyncio.run(self.execute_node_async(node_name, input_data))

    async def execute_node_async(self, node_name: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Async version of execute_node"""
        logger.info(f"Executing node: {node_name}")
        try:
            node = self.workflow_data['nodes'][node_name]
            node_type = node.get('type')
            node_data = node.copy()

            if input_data:
                node_data['input'] = input_data

            resolved_node_data = self.resolve_placeholders_for_execution(node_data)

            logger.info(f"Node type: {node_type}")
            logger.info(f"Node data after resolving placeholders: {self.log_safe_node_data(resolved_node_data)}")

            # Process the parameters to ensure correct types
            processed_data = self._process_node_parameters(resolved_node_data)

            # Check if 'params' is already in the data
            if 'params' in processed_data and isinstance(processed_data['params'], dict):
                # Parameters are already properly structured
                executor_data = processed_data
            else:
                # Extract node metadata from the parameters
                metadata = {k: v for k, v in processed_data.items() 
                        if k in ['type', 'label', 'position_x', 'position_y', 'description', 'input']}
                
                # Extract execution parameters (everything not in metadata)
                params = {k: v for k, v in processed_data.items() 
                        if k not in ['type', 'label', 'position_x', 'position_y', 'description', 'input']}
                
                # Create the data structure with params nested
                executor_data = metadata.copy()
                executor_data['params'] = params

            executor = self.node_executors.get(node_type)
            if executor:
                logger.info(f"Executor found for node type: {node_type}")

                # Check if the execute method is a coroutine function
                if inspect.iscoroutinefunction(executor.execute):
                    # If it's async, await it directly
                    result = await executor.execute(executor_data)
                else:
                    # If it's not async, check the result
                    result = executor.execute(executor_data)
                    
                    # If the result is a coroutine, await it
                    if inspect.iscoroutine(result):
                        result = await result
                    
                logger.info(f"Node {node_name} execution result: {self.log_safe_node_data(result)}")
                return result
            else:
                logger.error(f"No executor found for node type: {node_type}")
                return {"status": "error", "message": f"No executor found for node type: {node_type}"}

        except Exception as e:
            logger.error(f"Error executing node {node_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
    def _process_node_parameters(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process node parameters to ensure correct types for the node execution."""
        processed_data = node_data.copy()
        
        # Process string values that might need to be converted to other types
        for key, value in processed_data.items():
            if isinstance(value, str):
                # Handle JSON strings
                if key == 'messages' and value.startswith('[') and value.endswith(']'):
                    try:
                        processed_data[key] = json.loads(value)
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse JSON for key {key}: {value}")
                # Handle boolean values
                elif value.lower() in ('true', 'false'):
                    processed_data[key] = value.lower() == 'true'
                # Handle numeric values
                elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                    processed_data[key] = int(value)
                elif self._is_float(value):
                    processed_data[key] = float(value)
        
        return processed_data

    def _is_float(self, text: str) -> bool:
        """Check if a string can be converted to float."""
        try:
            float(text)
            return True
        except ValueError:
            return False

    def resolve_placeholders_for_execution(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve placeholders in node_data for execution."""
        if not node_data:
            return node_data
            
        resolved_data = {}
        
        for key, value in node_data.items():
            if isinstance(value, dict):
                resolved_data[key] = self.resolve_placeholders_for_execution(value)
            elif isinstance(value, list):
                resolved_data[key] = [
                    self.resolve_placeholders_for_execution(item) if isinstance(item, dict)
                    else self.resolve_placeholder_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                resolved_data[key] = self.resolve_placeholder_string(value)
            else:
                resolved_data[key] = value
                
        return resolved_data

    def resolve_placeholder_string(self, text: str) -> str:
        # Handle environment variables
        if text.startswith('${') and text.endswith('}'):
            env_var = text[2:-1]
            return os.environ.get(env_var, text)
        
        pattern = re.compile(r'\{\{(.*?)\}\}')
        matches = pattern.findall(text)
        
        for match in matches:
            parts = match.split('.')
            node_id = parts[0]
            path = '.'.join(parts[1:])
            value = self.fetch_value(node_id, path)
            if value is not None:
                text = text.replace(f"{{{{{match}}}}}", str(value))
        
        return text

    def fetch_value(self, node_id: str, path: str) -> Any:
        logger.info(f"Fetching value for node_id: {node_id}, path: {path}")
        if node_id in self.node_results:
            result = self.node_results[node_id]
            for part in path.split('.'):
                if isinstance(result, dict) and part in result:
                    result = result[part]
                else:
                    return None
            return result
        return None

    @staticmethod
    def log_safe_node_data(node_data):
        if isinstance(node_data, dict):
            # Redact sensitive keys like 'api_key' if needed
            safe_data = {k: ('[REDACTED]' if k == 'api_key' else v) for k, v in node_data.items()}
        else:
            safe_data = node_data
        return json.dumps(safe_data, indent=2)

    @classmethod
    def register_node_type(cls, node_type: str, node_class: Any):
        logger.info(f"Registering custom node type: {node_type}")
        if not hasattr(cls, 'custom_node_types'):
            cls.custom_node_types = {}
        cls.custom_node_types[node_type] = node_class

    def get_node_executor(self, node_type: str) -> Any:
        if hasattr(self, 'custom_node_types') and node_type in self.custom_node_types:
            return self.custom_node_types[node_type]()
        return self.node_executors.get(node_type)

    def _print_node_execution_results(self):
        """
        Print a formatted table showing the execution results of all nodes
        that have been executed so far (stored in self.node_results).
        """
        if not self.node_results:
            print("\nNo nodes have been executed yet.\n")
            return

        headers = ["Node Name", "Status", "Message"]
        table_data = []

        for node_name, node_result in self.node_results.items():
            status = node_result.get('status', 'unknown')
            message = node_result.get('message', '')
            
            # Determine symbol/color based on status
            if status == 'success':
                status_symbol = "🟢"
                status_color = Fore.GREEN
            elif status == 'error':
                status_symbol = "🔴"
                status_color = Fore.RED
            elif status == 'warning':
                status_symbol = "🟡"
                status_color = Fore.YELLOW
            else:
                status_symbol = "⚪"
                status_color = Fore.WHITE

            table_data.append([
                node_name,
                f"{status_color}{status_symbol} {status.upper()}{Style.RESET_ALL}",
                message
            ])

        table = tabulate(table_data, headers=headers, tablefmt="grid")
        print("\nNode Execution Results:")
        print(table)
        print()


if __name__ == "__main__":
    # This block is for testing the ExecutionManager class independently
    execution_manager = ExecutionManager(actfile_path='path/to/your/Actfile', sandbox_timeout=600)
    result = execution_manager.execute_workflow()
    print(json.dumps(result, indent=2))
"""
Claude Node - Interacts with Anthropic Claude API using the official SDK.
Provides access to Claude text generation, messages, and other Anthropic services.
"""

import logging
import json
import asyncio
import time
import os
from typing import Dict, Any, List, Optional, Union, Tuple

# Import Anthropic SDK
import anthropic

from base_node import (
    BaseNode, NodeSchema, NodeParameter, NodeParameterType,
    NodeValidationError
)

# Configure logging
logger = logging.getLogger(__name__)

class ClaudeModel:
    """Models available in Anthropic API."""
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    # Alias for latest models
    CLAUDE_LATEST = "claude-3-7-sonnet-20250219"
    # Legacy models
    CLAUDE_2_1 = "claude-2.1"
    CLAUDE_2_0 = "claude-2.0"
    CLAUDE_INSTANT_1_2 = "claude-instant-1.2"

class ClaudeOperation:
    """Operations available on Anthropic API."""
    MESSAGES = "messages"
    MESSAGE_STREAM = "message_stream"
    COMPLETION = "completion"
    COMPLETION_STREAM = "completion_stream"

class ClaudeNode(BaseNode):
    """
    Node for interacting with Anthropic Claude API using the official SDK.
    Provides functionality for text generation and other Claude services.
    """
    
    def __init__(self, sandbox_timeout: Optional[int] = None):
        super().__init__(sandbox_timeout=sandbox_timeout)
        self.client = None
        
    def get_schema(self) -> NodeSchema:
        """Return the schema definition for the Claude node."""
        return NodeSchema(
            node_type="claude",
            version="1.0.0",
            description="Interacts with Anthropic Claude API for AI text generation",
            parameters=[
                # Basic parameters
                NodeParameter(
                    name="operation",
                    type=NodeParameterType.STRING,
                    description="Operation to perform with Claude API",
                    required=True,
                    enum=[
                        ClaudeOperation.MESSAGES,
                        ClaudeOperation.MESSAGE_STREAM,
                        ClaudeOperation.COMPLETION,
                        ClaudeOperation.COMPLETION_STREAM
                    ]
                ),
                NodeParameter(
                    name="api_key",
                    type=NodeParameterType.STRING,
                    description="Anthropic API key",
                    required=True
                ),
                
                # Common parameters
                NodeParameter(
                    name="model",
                    type=NodeParameterType.STRING,
                    description="Claude model to use",
                    required=False,
                    default=ClaudeModel.CLAUDE_LATEST,
                    enum=[
                        ClaudeModel.CLAUDE_3_OPUS,
                        ClaudeModel.CLAUDE_3_SONNET,
                        ClaudeModel.CLAUDE_3_HAIKU,
                        ClaudeModel.CLAUDE_3_5_SONNET,
                        ClaudeModel.CLAUDE_3_7_SONNET,
                        ClaudeModel.CLAUDE_LATEST,
                        ClaudeModel.CLAUDE_2_1,
                        ClaudeModel.CLAUDE_2_0,
                        ClaudeModel.CLAUDE_INSTANT_1_2
                    ]
                ),
                NodeParameter(
                    name="max_tokens",
                    type=NodeParameterType.NUMBER,
                    description="Maximum number of tokens to generate",
                    required=False,
                    default=1024
                ),
                NodeParameter(
                    name="temperature",
                    type=NodeParameterType.NUMBER,
                    description="Temperature for generation (0-1)",
                    required=False,
                    default=0.7
                ),
                NodeParameter(
                    name="top_p",
                    type=NodeParameterType.NUMBER,
                    description="Top-p sampling parameter (0-1)",
                    required=False,
                    default=1.0
                ),
                NodeParameter(
                    name="top_k",
                    type=NodeParameterType.NUMBER,
                    description="Top-k sampling parameter",
                    required=False
                ),
                
                # Messages parameters
                NodeParameter(
                    name="messages",
                    type=NodeParameterType.ARRAY,
                    description="Messages for Claude API (for messages operation)",
                    required=False
                ),
                NodeParameter(
                    name="system",
                    type=NodeParameterType.STRING,
                    description="System message for Claude API",
                    required=False
                ),
                
                # Completion parameters
                NodeParameter(
                    name="prompt",
                    type=NodeParameterType.STRING,
                    description="Prompt for legacy completion API",
                    required=False
                ),
                
                # Media parameters
                NodeParameter(
                    name="input_images",
                    type=NodeParameterType.ARRAY,
                    description="Array of image objects to include in the message",
                    required=False
                ),
                
                # Advanced parameters
                NodeParameter(
                    name="stop_sequences",
                    type=NodeParameterType.ARRAY,
                    description="Sequences where Claude will stop generating",
                    required=False
                ),
                NodeParameter(
                    name="metadata",
                    type=NodeParameterType.OBJECT,
                    description="Metadata to include with the request",
                    required=False
                ),
                NodeParameter(
                    name="tool_choice",
                    type=NodeParameterType.ANY,
                    description="Controls which tool Claude uses",
                    required=False
                ),
                NodeParameter(
                    name="tools",
                    type=NodeParameterType.ARRAY,
                    description="List of tools the model may call",
                    required=False
                ),
                NodeParameter(
                    name="response_format",
                    type=NodeParameterType.OBJECT,
                    description="Format to return the response in",
                    required=False
                ),
            ],
            
            # Define outputs for the node
            outputs={
                "status": NodeParameterType.STRING,
                "result": NodeParameterType.ANY,
                "error": NodeParameterType.STRING,
                "usage": NodeParameterType.OBJECT,
                "model": NodeParameterType.STRING,
                "created_at": NodeParameterType.NUMBER
            },
            
            # Add metadata
            tags=["ai", "claude", "anthropic", "nlp", "text-generation"],
            author="System"
        )
    
    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation based on the operation type."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if not operation:
            raise NodeValidationError("Operation is required")
            
        # Check for API key
        if not params.get("api_key"):
            raise NodeValidationError("Anthropic API key is required")
            
        # Validate based on operation
        if operation in [ClaudeOperation.MESSAGES, ClaudeOperation.MESSAGE_STREAM]:
            if not params.get("messages") and not params.get("system"):
                raise NodeValidationError("Either messages or system parameter is required for messages operation")
                
            # Validate messages format if provided
            messages = params.get("messages", [])
            if messages and not isinstance(messages, list):
                raise NodeValidationError("Messages must be an array")
                
            for msg in messages:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    raise NodeValidationError("Each message must have 'role' and 'content' fields")
                
            # Validate temperature
            temperature = params.get("temperature", 0.7)
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 1:
                raise NodeValidationError("Temperature must be between 0 and 1")
                
        elif operation in [ClaudeOperation.COMPLETION, ClaudeOperation.COMPLETION_STREAM]:
            if not params.get("prompt"):
                raise NodeValidationError("Prompt is required for completion operation")
        
        return {}
    
    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Claude node."""
        try:
            # Validate schema and parameters
            validated_data = self.validate_schema(node_data)
            
            # Get operation type
            operation = validated_data.get("operation")
            
            # Initialize Anthropic client
            api_key = validated_data.get("api_key")
            
            # Create Anthropic client without anthropic_version parameter
            self.client = anthropic.Anthropic(api_key=api_key)
            
            # Execute the appropriate operation
            if operation == ClaudeOperation.MESSAGES:
                return await self._operation_messages(validated_data)
            elif operation == ClaudeOperation.MESSAGE_STREAM:
                return await self._operation_message_stream(validated_data)
            elif operation == ClaudeOperation.COMPLETION:
                return await self._operation_completion(validated_data)
            elif operation == ClaudeOperation.COMPLETION_STREAM:
                return await self._operation_completion_stream(validated_data)
            else:
                error_message = f"Unknown operation: {operation}"
                logger.error(error_message)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_message,
                    "usage": None,
                    "model": None,
                    "created_at": None
                }
                
        except Exception as e:
            error_message = f"Error in Claude node: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "usage": None,
                "model": None,
                "created_at": None
            }
    
    # -------------------------
    # Operation Methods
    # -------------------------
    
    async def _operation_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a messages request to the Claude API.
        
        Args:
            params: Messages parameters
            
        Returns:
            Messages results
        """
        # Extract parameters
        model = params.get("model", ClaudeModel.CLAUDE_LATEST)
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        top_p = params.get("top_p", 1.0)
        top_k = params.get("top_k")
        
        # Get messages from parameters
        messages = params.get("messages", [])
        system = params.get("system")
        
        # Process input images if any
        input_images = params.get("input_images", [])
        if input_images and isinstance(messages, list) and len(messages) > 0:
            # Find the user message to add images to
            for i, msg in enumerate(messages):
                if msg.get("role") == "user":
                    # If content is a string, convert to list format
                    if isinstance(msg["content"], str):
                        msg["content"] = [{"type": "text", "text": msg["content"]}]
                    
                    # Add images to content if it's a list
                    if isinstance(msg["content"], list):
                        for image in input_images:
                            if isinstance(image, dict) and "url" in image:
                                msg["content"].append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64" if image.get("type") == "base64" else "url",
                                        "media_type": image.get("media_type", "image/jpeg"),
                                        "data": image["url"]
                                    }
                                })
                    break
        
        # Advanced parameters
        stop_sequences = params.get("stop_sequences")
        metadata = params.get("metadata")
        tools = params.get("tools")
        tool_choice = params.get("tool_choice")
        response_format = params.get("response_format")
        
        # Build request
        request_args = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": messages,
        }
        
        # Add system message if provided
        if system:
            request_args["system"] = system
        
        # Add optional parameters
        if top_k is not None:
            request_args["top_k"] = top_k
        if stop_sequences:
            request_args["stop_sequences"] = stop_sequences
        if metadata:
            request_args["metadata"] = metadata
        if tools:
            request_args["tools"] = tools
        if tool_choice:
            request_args["tool_choice"] = tool_choice
        if response_format:
            request_args["response_format"] = response_format
        
        try:
            # Send request
            start_time = time.time()
            response = await asyncio.to_thread(self.client.messages.create, **request_args)
            
            # Process response
            result = {}
            if hasattr(response, 'model_dump'):
                result = response.model_dump()
            else:
                # Convert response to dict if model_dump not available
                result = response.dict() if hasattr(response, 'dict') else dict(response)
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "usage": result.get("usage"),
                "model": model,
                "created_at": int(start_time)
            }
            
        except Exception as e:
            error_message = f"Claude messages error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "usage": None,
                "model": model,
                "created_at": None
            }
    
    async def _operation_message_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a streaming messages request to the Claude API.
        
        Args:
            params: Messages parameters
            
        Returns:
            Streamed messages results
        """
        # Extract parameters
        model = params.get("model", ClaudeModel.CLAUDE_LATEST)
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        top_p = params.get("top_p", 1.0)
        top_k = params.get("top_k")
        
        # Get messages from parameters
        messages = params.get("messages", [])
        system = params.get("system")
        
        # Process input images if any
        input_images = params.get("input_images", [])
        if input_images and isinstance(messages, list) and len(messages) > 0:
            # Find the user message to add images to
            for i, msg in enumerate(messages):
                if msg.get("role") == "user":
                    # If content is a string, convert to list format
                    if isinstance(msg["content"], str):
                        msg["content"] = [{"type": "text", "text": msg["content"]}]
                    
                    # Add images to content if it's a list
                    if isinstance(msg["content"], list):
                        for image in input_images:
                            if isinstance(image, dict) and "url" in image:
                                msg["content"].append({
                                    "type": "image",
                                    "source": {
                                        "type": "base64" if image.get("type") == "base64" else "url",
                                        "media_type": image.get("media_type", "image/jpeg"),
                                        "data": image["url"]
                                    }
                                })
                    break
        
        # Advanced parameters
        stop_sequences = params.get("stop_sequences")
        metadata = params.get("metadata")
        tools = params.get("tools")
        tool_choice = params.get("tool_choice")
        response_format = params.get("response_format")
        
        # Build request
        request_args = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": messages,
            "stream": True
        }
        
        # Add system message if provided
        if system:
            request_args["system"] = system
        
        # Add optional parameters
        if top_k is not None:
            request_args["top_k"] = top_k
        if stop_sequences:
            request_args["stop_sequences"] = stop_sequences
        if metadata:
            request_args["metadata"] = metadata
        if tools:
            request_args["tools"] = tools
        if tool_choice:
            request_args["tool_choice"] = tool_choice
        if response_format:
            request_args["response_format"] = response_format
        
        try:
            # Send streaming request
            start_time = time.time()
            stream = await asyncio.to_thread(self.client.messages.create, **request_args)
            
            # Collect stream chunks - using updated delta structure
            full_content = ""
            content_blocks = []
            last_message = None
            
            async def process_stream():
                nonlocal full_content, content_blocks, last_message
                
                # Process each chunk in the stream
                for chunk in stream:
                    # Different structure in the new SDK
                    if hasattr(chunk, "delta") and hasattr(chunk.delta, "content"):
                        if chunk.delta.content is not None:
                            delta_content = chunk.delta.content
                            full_content += delta_content
                            content_blocks.append(delta_content)
                    elif hasattr(chunk, "content_block") and hasattr(chunk.content_block, "text"):
                        # Alternative structure that might be present
                        delta_content = chunk.content_block.text
                        full_content += delta_content
                        content_blocks.append(delta_content)
                    elif hasattr(chunk, "message"):
                        # Save the most recent message
                        last_message = chunk.message
                    
                    # Yield to event loop occasionally
                    await asyncio.sleep(0)
                
                return full_content
            
            # Wait for stream to complete
            content = await process_stream()
            
            # Format into a complete response
            if last_message:
                if hasattr(last_message, 'dict'):
                    result = last_message.dict()
                elif hasattr(last_message, 'model_dump'):
                    result = last_message.model_dump()
                else:
                    result = dict(last_message)
            else:
                # Fallback if no complete message was received
                result = {
                    "content": content,
                    "role": "assistant",
                    "model": model,
                    "stop_reason": "end_turn",
                    "type": "message"
                }
            
            # Add additional streaming info
            streaming_info = {
                "chunks_received": len(content_blocks),
                "content_blocks": content_blocks[:5] + ["..."] if len(content_blocks) > 5 else content_blocks,
                "streaming_duration": time.time() - start_time
            }
            
            return {
                "status": "success",
                "result": result,
                "streaming_info": streaming_info,
                "usage": result.get("usage"),
                "model": model,
                "created_at": int(start_time)
            }
            
        except Exception as e:
            error_message = f"Claude message stream error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "usage": None,
                "model": model,
                "created_at": None
            }
    
    async def _operation_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a completion request to the Claude API (legacy).
        
        Args:
            params: Completion parameters
            
        Returns:
            Completion results
        """
        # Extract parameters
        model = params.get("model", ClaudeModel.CLAUDE_LATEST)
        prompt = params.get("prompt")
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        top_p = params.get("top_p", 1.0)
        top_k = params.get("top_k")
        stop_sequences = params.get("stop_sequences")
        
        # Format with Claude prompt requirements (legacy API)
        formatted_prompt = f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"
        
        # Build request
        request_args = {
            "model": model,
            "prompt": formatted_prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        
        # Add optional parameters
        if top_k is not None:
            request_args["top_k"] = top_k
        if stop_sequences:
            request_args["stop_sequences"] = stop_sequences
        
        try:
            # Send request
            start_time = time.time()
            response = await asyncio.to_thread(self.client.completions.create, **request_args)
            
            # Process response
            if hasattr(response, 'model_dump'):
                result = response.model_dump()
            elif hasattr(response, 'dict'):
                result = response.dict()
            else:
                result = dict(response)
            
            # Format the response
            return {
                "status": "success",
                "result": result,
                "usage": None,  # Legacy API doesn't provide usage stats
                "model": model,
                "created_at": int(start_time)
            }
            
        except Exception as e:
            error_message = f"Claude completion error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "usage": None,
                "model": model,
                "created_at": None
            }
    
    async def _operation_completion_stream(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a streaming completion request to the Claude API (legacy).
        
        Args:
            params: Completion parameters
            
        Returns:
            Streamed completion results
        """
        # Extract parameters
        model = params.get("model", ClaudeModel.CLAUDE_LATEST)
        prompt = params.get("prompt")
        max_tokens = params.get("max_tokens", 1024)
        temperature = params.get("temperature", 0.7)
        top_p = params.get("top_p", 1.0)
        top_k = params.get("top_k")
        stop_sequences = params.get("stop_sequences")
        
        # Format with Claude prompt requirements (legacy API)
        formatted_prompt = f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"
        
        # Build request
        request_args = {
            "model": model,
            "prompt": formatted_prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True
        }
        
        # Add optional parameters
        if top_k is not None:
            request_args["top_k"] = top_k
        if stop_sequences:
            request_args["stop_sequences"] = stop_sequences
        
        try:
            # Send streaming request
            start_time = time.time()
            stream = await asyncio.to_thread(self.client.completions.create, **request_args)
            
            # Collect stream chunks
            full_content = ""
            content_blocks = []
            
            async def process_stream():
                nonlocal full_content, content_blocks
                
                # Process each chunk in the stream
                for chunk in stream:
                    if hasattr(chunk, "completion"):
                        # For completion API, the chunk has the delta in the completion field
                        delta = chunk.completion
                        full_content += delta
                        content_blocks.append(delta)
                    
                    # Yield to event loop occasionally
                    await asyncio.sleep(0)
                
                # Return collected content
                return full_content
            
            # Wait for stream to complete
            content = await process_stream()
            
            # Format into a complete response
            result = {
                "completion": content,
                "model": model,
                "stop_reason": "stop_sequence",
                "type": "completion"
            }
            
            # Add additional streaming info
            streaming_info = {
                "chunks_received": len(content_blocks),
                "content_blocks": content_blocks[:5] + ["..."] if len(content_blocks) > 5 else content_blocks,
                "streaming_duration": time.time() - start_time
            }
            
            return {
                "status": "success",
                "result": result,
                "streaming_info": streaming_info,
                "usage": None,  # Legacy API doesn't provide usage stats
                "model": model,
                "created_at": int(start_time)
            }
            
        except Exception as e:
            error_message = f"Claude completion stream error: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "result": None,
                "error": error_message,
                "usage": None,
                "model": model,
                "created_at": None
            }


# Main test function for Claude Node
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create async test runner
    async def run_tests():
        print("=== Claude Node Test Suite ===")
        
        # Get API key from environment or user input
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            api_key = input("Enter Anthropic API key: ")
            if not api_key:
                print("API key is required for testing")
                return
        
        # Create an instance of the Claude Node
        node = ClaudeNode()
        
        # Test cases - only run if API key provided
        test_cases = [
            {
                "name": "Messages API - Basic Text",
                "params": {
                    "operation": ClaudeOperation.MESSAGES,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_HAIKU,
                    "messages": [
                        {"role": "user", "content": "What's the square root of 144 and why?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                "expected_status": "success"
            },
            {
                "name": "Messages API - System Prompt",
                "params": {
                    "operation": ClaudeOperation.MESSAGES,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_HAIKU,
                    "system": "You are a mathematics tutor providing very concise answers",
                    "messages": [
                        {"role": "user", "content": "Explain the concept of a prime number briefly"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                "expected_status": "success"
            },
            {
                "name": "Messages API - Conversation",
                "params": {
                    "operation": ClaudeOperation.MESSAGES,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_HAIKU,
                    "messages": [
                        {"role": "user", "content": "Hello, I want to learn about Mars."},
                        {"role": "assistant", "content": "Hi there! I'd be happy to help you learn about Mars. What specifically would you like to know about the red planet?"},
                        {"role": "user", "content": "How long is a day on Mars?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                "expected_status": "success"
            },
            {
                "name": "Message Stream API",
                "params": {
                    "operation": ClaudeOperation.MESSAGE_STREAM,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_HAIKU,
                    "messages": [
                        {"role": "user", "content": "Write a 5-word poem about programming"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 30
                },
                "expected_status": "success"
            },
            {
                "name": "Completion API (Legacy)",
                "params": {
                    "operation": ClaudeOperation.COMPLETION,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_2_1,
                    "prompt": "What's the capital of France?",
                    "temperature": 0.7,
                    "max_tokens": 50
                },
                "expected_status": "success"
            }
        ]
        
        # Run all test cases with a delay between tests
        total_tests = len(test_cases)
        passed_tests = 0
        
        for test_case in test_cases:
            print(f"\nRunning test: {test_case['name']}")
            
            try:
                # Prepare node data
                node_data = {
                    "params": test_case["params"]
                }
                
                # Execute the node
                result = await node.execute(node_data)
                
                # Check if the result status matches expected status
                if result["status"] == test_case["expected_status"]:
                    print(f"✅ PASS: {test_case['name']} - Status: {result['status']}")
                    if result["result"]:
                        if isinstance(result["result"], dict) and "content" in result["result"]:
                            content = result["result"]["content"]
                            if isinstance(content, list):
                                content = " ".join([item.get("text", "") for item in content])
                            print(f"Response content: {content[:150]}...")
                        else:
                            print(f"Response preview: {str(result['result'])[:150]}...")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: {test_case['name']} - Expected status {test_case['expected_status']}, got {result['status']}")
                    print(f"Error: {result.get('error')}")
                    
                # Add a delay between tests to avoid rate limiting
                await asyncio.sleep(2.0)
                
            except Exception as e:
                print(f"❌ FAIL: {test_case['name']} - Exception: {str(e)}")
        
        # Print summary
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests / total_tests * 100:.1f}%")
        
        # Optional manual test for vision capabilities
        run_vision_test = input("\nRun vision test with Claude? (y/n): ").lower() == 'y'
        if run_vision_test:
            print("\n=== Manual Test: Claude Vision Capabilities ===")
            image_url = input("Enter a publicly accessible image URL to analyze (or press Enter for default test image): ")
            
            # Use a default image if none provided
            if not image_url:
                image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                print(f"Using default test image: {image_url}")
            
            # Set up vision test
            vision_prompt = input("Enter a prompt about the image (or press Enter for default prompt): ")
            if not vision_prompt:
                vision_prompt = "What do you see in this image? Describe it in detail."
                print(f"Using default prompt: {vision_prompt}")
                
            vision_result = await node.execute({
                "params": {
                    "operation": ClaudeOperation.MESSAGES,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_HAIKU,  # Haiku supports vision too and is faster
                    "messages": [
                        {"role": "user", "content": vision_prompt}
                    ],
                    "input_images": [
                        {"type": "url", "url": image_url, "media_type": "image/jpeg"}
                    ],
                    "max_tokens": 300
                }
            })
            
            if vision_result["status"] == "success":
                print("✅ Vision test successful")
                if "content" in vision_result["result"]:
                    content = vision_result["result"]["content"]
                    if isinstance(content, list):
                        content = " ".join([item.get("text", "") for item in content if item.get("type") == "text"])
                    print(f"\nVision Analysis:\n{content}")
                else:
                    print(f"Response preview: {str(vision_result['result'])[:250]}...")
            else:
                print(f"❌ Vision test failed: {vision_result.get('error')}")
        
        # Tool usage test
        run_tool_test = input("\nRun tool usage test with Claude? (y/n): ").lower() == 'y'
        if run_tool_test:
            print("\n=== Manual Test: Claude Tool Usage ===")
            
            # Define a simple calculator tool
            calculator_tool = {
                "name": "calculator",
                "description": "Performs basic arithmetic calculations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The arithmetic expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
            
            tool_result = await node.execute({
                "params": {
                    "operation": ClaudeOperation.MESSAGES,
                    "api_key": api_key,
                    "model": ClaudeModel.CLAUDE_3_SONNET,  # Use Sonnet for better tool usage
                    "messages": [
                        {"role": "user", "content": "Calculate 24 * 15 + 312"}
                    ],
                    "tools": [calculator_tool],
                    "tool_choice": {"type": "auto"},
                    "max_tokens": 200
                }
            })
            
            if tool_result["status"] == "success":
                print("✅ Tool usage test successful")
                
                # Extract tool calls if available
                if "content" in tool_result["result"]:
                    print(f"\nTool Usage Result:\n{json.dumps(tool_result['result'], indent=2)[:500]}...")
                else:
                    print(f"Response preview: {str(tool_result['result'])[:250]}...")
            else:
                print(f"❌ Tool usage test failed: {tool_result.get('error')}")
        
        print("\nAll tests completed!")

    # Run the async tests
    asyncio.run(run_tests())
    
# Register with NodeRegistry
try:
    from node_registry import NodeRegistry
    # Create registry instance and register the node
    registry = NodeRegistry()
    registry.register("claude", ClaudeNode)
    logger.info("Successfully registered ClaudeNode with registry")
except ImportError:
    logger.warning("Could not register ClaudeNode with registry - module not found")
except Exception as e:
    logger.error(f"Error registering ClaudeNode with registry: {str(e)}")
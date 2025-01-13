import logging

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from functools import wraps

from src.models.core import ChatRequest, AgentResponse


def handle_exceptions(func):
    """Decorator to handle exceptions uniformly across agent methods"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ValueError as e:
            # Handle validation errors - these are expected and should return as needs_info
            self.logger.info(f"Validation error in {func.__name__}: {str(e)}")
            return AgentResponse.error(error_message=str(e))
        except Exception as e:
            # Handle unexpected errors - these are breaking errors
            self.logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message="An unexpected error occurred. Please try again later.")

    return wrapper


class AgentCore(ABC):
    """Enhanced core agent functionality that all specialized agents inherit from."""

    def __init__(self, config: Dict[str, Any], llm: Any, embeddings: Any):
        self.config = config
        self.llm = llm
        self.embeddings = embeddings
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging for the agent"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def _validate_request(self, request: ChatRequest) -> Optional[AgentResponse]:
        """Validate common request parameters and return appropriate response type"""
        if not request.prompt:
            return AgentResponse.error(error_message="Please provide a prompt to process your request")

        return None

    @handle_exceptions
    async def chat(self, request: ChatRequest) -> AgentResponse:
        """Main entry point for chat interactions"""
        self.logger.info(f"Received chat request: {request}")

        # Validate request
        validation_result = await self._validate_request(request)
        if validation_result:
            return validation_result

        # Process the request
        response = await self._process_request(request)

        # Log response for monitoring
        if response.error_message:
            self.logger.warning(f"Response error: {response.error_message}")

        return response

    @abstractmethod
    async def _process_request(self, request: ChatRequest) -> AgentResponse:
        """
        Process the validated request. Must be implemented by subclasses.

        Args:
            request: Validated ChatRequest object

        Returns:
            AgentResponse: Response containing content and optional error/metadata
        """
        raise NotImplementedError("Subclasses must implement _process_request")

    async def _handle_llm_response(self, response: Any) -> AgentResponse:
        """Handle LLM response and convert to appropriate AgentResponse"""
        try:
            if not response:
                return AgentResponse.error(
                    error_message="I couldn't process that request. Could you please rephrase it?"
                )

            # Extract relevant information from LLM response
            content = getattr(response, "content", None)
            tool_calls = getattr(response, "tool_calls", [])
            if tool_calls:
                # Handle tool calls
                self.logger.info(f"Processing tool calls: {tool_calls}")
                return await self._process_tool_calls(tool_calls)
            elif content:
                # Direct response from LLM
                self.logger.info(f"Received direct response from LLM: {content}")
                return AgentResponse.success(content=content)
            else:
                self.logger.warning("Received invalid response format from LLM")
                return AgentResponse.error(error_message="Received invalid response format from LLM")

        except Exception as e:
            self.logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message="Error processing the response")

    async def _process_tool_calls(self, tool_calls: list) -> AgentResponse:
        """Process tool calls from LLM response"""
        try:
            tool_call = tool_calls[0]  # Get first tool call
            func_name = tool_call.get("name")
            args = tool_call.get("args", {})

            if not func_name:
                return AgentResponse.error(error_message="Invalid tool call format - no function name provided")

            # Execute tool and handle response
            # This should be implemented by subclasses based on their specific tools
            return await self._execute_tool(func_name, args)

        except Exception as e:
            self.logger.error(f"Error processing tool calls: {str(e)}", exc_info=True)
            return AgentResponse.error(error_message="Error executing the requested action")

    @abstractmethod
    async def _execute_tool(self, func_name: str, args: Dict[str, Any]) -> AgentResponse:
        """Execute a tool with given arguments. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _execute_tool")

"""Stripe Agent Toolkit."""

from typing import List, Optional
from pydantic import PrivateAttr
import json
from openai.types.chat import ChatCompletion, ChatCompletionToolParam, ChatCompletionToolMessageParam, ChatCompletionMessageToolCall


from ..api import StripeAPI
from ..tools import tools
from ..configuration import Configuration, is_tool_allowed


class StripeAgentToolkit:
    _tools: List[ChatCompletionToolParam] = PrivateAttr(default=[])
    _stripe_api: StripeAPI

    def __init__(
        self, secret_key: str, configuration: Optional[Configuration] = None
    ):
        super().__init__()

        context = configuration.get("context") if configuration else None

        self._stripe_api = StripeAPI(secret_key=secret_key, context=context)
        
        filtered_tools = [
            tool for tool in tools if is_tool_allowed(tool, configuration)
        ]

        self._tools = [
            {"type": "function",
             "function": {
                 "name": tool["method"],
                 "description": tool["description"],
                 "parameters": tool["args_schema"].model_json_schema()
             }}
            for tool in filtered_tools
        ]

    def get_tools(self) -> List[ChatCompletionToolParam]:
        """Get the tools in the toolkit."""
        return self._tools
    
    def handle_tool_call(self, tool_call: ChatCompletionMessageToolCall) -> ChatCompletionToolMessageParam:
        """Process a single OpenAI tool call and return its execution result.
        
        This method takes a tool call object, extracts and parses its arguments, 
        executes the corresponding API function, and formats the response
        as a tool message for the chat completion.
        
        Args:
            tool_call: A ChatCompletionMessageToolCall object containing the function
                    name and arguments to be executed.
                    
        Returns:
            A dictionary containing the tool execution result in the format
            required by the chat completion API, including role, tool_call_id,
            and content fields.
        """
        args = json.loads(tool_call.function.arguments)
        response = self._stripe_api.run(tool_call.function.name, **args)
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": response
        }
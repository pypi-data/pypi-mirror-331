# Standard library imports
import base64
import copy
from dataclasses import dataclass, field
import json
from collections import defaultdict
from typing import Callable, Optional, Union, Coroutine, Any
import inspect
import asyncio
import logging

# Package/library imports
from litellm import acompletion
from litellm.types.completion import ChatCompletionMessageToolCallParam, Function
from pydantic import BaseModel

# Local imports
from .util import function_to_json, get_mime_type_from_file_like_object, merge_chunk, type_to_response_format

# Configure logger
logger = logging.getLogger(__name__)

# Types
AgentFunction = Callable[..., Union[str, "Agent", dict, Coroutine[Any, Any, Union[str, "Agent", dict]]]]

@dataclass
class Response():
    value: Any
    messages: list
    agent: "Agent"

@dataclass
class Result():
    """
    Encapsulates the possible return values for an agent tool call.

    Attributes:
        value (str): The result value as a string.
        agent (Agent): The agent instance, if applicable.
        add_to_memory (bool): Whether to add the result to the memory. Defaults to True if no agent is provided,
                            and False if an agent is provided.
        exit (bool): Whether to exit the current agent and return the result as the final answer. Defaults to False.
    """

    value: str = ""
    agent: Optional["Agent"] = None
    add_to_memory: bool = field(default_factory=lambda: True)
    exit: bool = False
    def __post_init__(self):
        # Override add_to_memory default if not explicitly set and agent is present
        if self.agent is not None and self.add_to_memory is True:
            self.add_to_memory = False

@dataclass
class HandleToolCallResult():
    messages: list
    agent: Optional["Agent"] = None
    filtered_tool_calls: list[ChatCompletionMessageToolCallParam] = field(default_factory=list)
    result: Optional[Result] = None

# Agent class

DEFAULT_MODEL = "gpt-4o"

class Agent:
    def __init__(
            self, 
            name: Optional[str] = None, 
            model: Optional[str] = None,
            instructions: Optional[Union[str, Callable[[], str]]] = None, 
            memory: Optional[list[dict]] = None,
            tools: Optional[list[AgentFunction]] = None, 
            tool_choice: Optional[Union[str, dict]] = None, 
            parallel_tool_calls: Optional[bool] = None, 
            response_format: Optional[Union[dict, type[BaseModel]]] = None,
            temperature: Optional[float] = None,
            top_p: Optional[float] = None,
            stop: Optional[list[str]] = None,
            max_completion_tokens: Optional[int] = None,
            **extra_llm_params
    ):
        self._name = name or self.__class__.__name__
        self._model = model or DEFAULT_MODEL
        self._instructions = instructions
        self._memory = memory or []
        self._tools = tools or []
        self._tool_choice = tool_choice
        self._parallel_tool_calls = parallel_tool_calls
        self._response_format = response_format
        self._temperature = temperature
        self._top_p = top_p
        self._stop = stop
        self._max_completion_tokens = max_completion_tokens
        self._extra_llm_params = extra_llm_params

        # Create a logger specific to this agent instance
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}(name='{self._name}')")
        self.logger.setLevel(logger.level)

        # Cache related
        self.__tools = None
        self.__json_tools = None
        self.__json_response_format = None
        self.__all_chat_completion_params = None
        
    @property 
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def model(self):
        return self._model
    @model.setter
    def model(self, value):
        if value != self._model:
            self.__all_chat_completion_params = None
            self._model = value

    @property
    def instructions(self):
        return self._instructions
    @instructions.setter
    def instructions(self, value):
        if value != self._instructions:
            self.__all_chat_completion_params = None
            self._instructions = value

    @property
    def memory(self):
        return self._memory
    @memory.setter
    def memory(self, value):
        self._memory = value

    @property
    def tools(self):
        return self._tools
    @tools.setter
    def tools(self, value):
        if value != self._tools:
            self.__all_chat_completion_params = None
            self.__json_tools = None
            self._tools = value 

    @property
    def tool_choice(self):
        return self._tool_choice
    @tool_choice.setter
    def tool_choice(self, value):
        if value != self._tool_choice:
            self.__all_chat_completion_params = None
            self._tool_choice = value

    @property
    def parallel_tool_calls(self):
        return self._parallel_tool_calls
    @parallel_tool_calls.setter
    def parallel_tool_calls(self, value):
        if value != self._parallel_tool_calls:
            self.__all_chat_completion_params = None
            self._parallel_tool_calls = value

    @property
    def response_format(self):
        return self._response_format
    @response_format.setter
    def response_format(self, value):
        if value != self._response_format:
            self.__all_chat_completion_params = None
            self.__json_response_format = None
            self._response_format = value

    @property
    def temperature(self):
        return self._temperature
    @temperature.setter
    def temperature(self, value):
        if value != self._temperature:
            self.__all_chat_completion_params = None
            self._temperature = value

    @property
    def top_p(self):
        return self._top_p
    @top_p.setter
    def top_p(self, value):
        if value != self._top_p:
            self.__all_chat_completion_params = None
            self._top_p = value

    @property
    def max_completion_tokens(self):
        return self._max_completion_tokens
    @max_completion_tokens.setter
    def max_completion_tokens(self, value):
        if value != self._max_completion_tokens:
            self.__all_chat_completion_params = None
            self._max_completion_tokens = value

    @property
    def extra_llm_params(self):
        return self._extra_llm_params
    @extra_llm_params.setter
    def extra_llm_params(self, value):
        if value != self._extra_llm_params:
            self.__all_chat_completion_params = None
            self._extra_llm_params = value


    def __get_all_chat_completion_params(self):
        if self.__all_chat_completion_params is not None:
            if self.__tools == self.tools:
                # It's safe to return the cached params
                return self.__all_chat_completion_params
            else:
                # Tools list has changed from the "outside". Make sure to update the cache afterwards.
                self.__tools = None
                self.__json_tools = None
        if self.__tools != self.tools:
            # Tools list has changed from the "outside"
            self.__tools = self.tools
            if self.tools:
                self.__json_tools = [function_to_json(f) for f in self.tools]
            else:
                self.__json_tools = None
        if self.__json_response_format is None:
            # Response format is updated, so we need to update the cached JSON response format
            self.__json_response_format = type_to_response_format(self.response_format)
        params = {}
        if self._extra_llm_params:
            params.update(self._extra_llm_params)
        params.update({
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_completion_tokens": self.max_completion_tokens,
        })
        if self.__json_tools:
            params.update({
                "tools": self.__json_tools,
                "tool_choice": self.tool_choice,
                "parallel_tool_calls": self.parallel_tool_calls,
            })
        if self.__json_response_format:
            params["response_format"] = self.__json_response_format
        return params


    async def get_chat_completion(self, stream: bool = False):
        if self.instructions:
            messages = [{"role": "system", "content": self.instructions}]
        else:
            messages = []
        messages.extend(self.memory)
        self.logger.debug("Getting chat completion for: %s", messages)

        create_params = self.__get_all_chat_completion_params().copy()
        create_params["messages"] = messages
        create_params["stream"] = stream

        return await acompletion(**create_params)


    async def handle_function_result(self, result) -> Result:
        if isinstance(result, Result):
            return result
        elif isinstance(result, Agent):
            return Result(
                value=json.dumps({"assistant": result.name}),
                agent=result,
            )
        else:
            try:
                return Result(value=str(result))
            except Exception as e:
                error_message = "Failed to cast response to string: %s. Make sure agent functions return a string, Result object, or coroutine. Error: %s"
                self.logger.error(error_message, result, str(e))
                raise TypeError(error_message % (result, str(e)))
            

    def get_value(self, content: str):
        if self.response_format:
            if isinstance(self.response_format, dict):
                return json.loads(content)
            elif issubclass(self.response_format, BaseModel):
                return self.response_format.model_validate_json(content)
            else:
                raise ValueError(f"Unsupported response_format: {self.response_format}")
        else:
            return content


    def update_partial_response(
            self, 
            partial_response: HandleToolCallResult, 
            tool_call: ChatCompletionMessageToolCallParam, 
            result: Result
    ) -> None:
        if result.add_to_memory:
            partial_response.filtered_tool_calls.append(tool_call)
            partial_response.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "tool_name": tool_call["function"]["name"],
                    "content": result.value,
                }
            )
        if result.agent:
            partial_response.agent = result.agent
        if result.exit:
            partial_response.result = result


    def _before_chat_completion(self) -> None:
        pass

    async def handle_tool_calls(
            self,
            tool_calls: list[ChatCompletionMessageToolCallParam],
    ) -> HandleToolCallResult:
        function_map = {f.__name__: f for f in self.tools}
        partial_response = HandleToolCallResult(messages=[], agent=None, filtered_tool_calls=[])

        async_tasks = []
        for tool_call in tool_calls:
            function = tool_call["function"]
            name = function["name"]
            if name not in function_map:
                self.logger.warning("Tool %s not found in function map.", name)
                self.update_partial_response(partial_response, tool_call, Result(value=f"Error: Tool {name} not found."))
                continue            
            
            args = json.loads(function["arguments"])

            func = function_map[name]
            
            if self.logger.level == logging.DEBUG:
                self.logger.debug("Processing tool call: %s with arguments %s", name, args)
            else:
                self.logger.info("Processing tool call: %s", name)
            raw_result = func(**args)
            if inspect.iscoroutine(raw_result):
                # Store coroutine with its metadata for parallel execution
                self.logger.info("Async tool call found: %s", name)
                async def tool_call_wrapper(raw_result):
                    self.logger.info("Processing async tool call: %s", name)
                    ret = await raw_result
                    if self.logger.level == logging.DEBUG:
                        self.logger.debug("Async tool call %s returned %s", name, ret)
                    else:
                        self.logger.info("Async tool call %s returned successfully", name)
                    return ret
                async_tasks.append((tool_call, tool_call_wrapper(raw_result)))
            else:
                if self.logger.level == logging.DEBUG:
                    self.logger.debug("Tool call %s returned %s", name, raw_result)
                else:
                    self.logger.info("Tool call %s returned successfully", name)
                # Handle synchronous results immediately
                result = await self.handle_function_result(raw_result)
                self.update_partial_response(partial_response, tool_call, result)
                if partial_response.result:
                    break

        # Execute async tasks in parallel if any exist
        if async_tasks:
            raw_results = await asyncio.gather(*(task[1] for task in async_tasks))
            for (tool_call, _), raw_result in zip(async_tasks, raw_results):
                result = await self.handle_function_result(raw_result)
                self.update_partial_response(partial_response, tool_call, result)
                if partial_response.result:
                    break

        # TODO: Cancel all pending async tasks if the result is a final answer

        return partial_response


    async def _run_and_stream(
            self,
            max_turns: int,
            execute_tools: bool,
    ):
        active_agent = self
        memory = self.memory
        init_len = len(memory)

        while len(memory) - init_len < max_turns:
            self._before_chat_completion()
            message = {
                "content": "",
                "sender": active_agent.name,
                "role": "assistant",
                "function_call": None,
                "tool_calls": defaultdict(
                    lambda: {
                        "function": {"arguments": "", "name": ""},
                        "id": "",
                        "type": "",
                    }
                ),
            }

            # get completion with current history, agent
            completion = await active_agent.get_chat_completion(stream=True)

            yield {"delim": "start"}
            async for chunk in completion:
                delta = json.loads(chunk.choices[0].delta.json())
                if delta["role"] == "assistant":
                    delta["sender"] = active_agent.name
                yield delta
                delta.pop("role", None)
                delta.pop("sender", None)
                merge_chunk(message, delta)
            yield {"delim": "end"}

            message["tool_calls"] = list(
                message.get("tool_calls", {}).values())
            if not message["tool_calls"]:
                message["tool_calls"] = None
            active_agent.logger.debug("Received completion: %s", message)
            memory.append(message)

            if not message["tool_calls"] or not execute_tools:
                active_agent.logger.debug("Ending turn.")
                break

            # convert tool_calls to objects
            tool_calls = []
            for tool_call in message["tool_calls"]:
                function = Function(
                    arguments=tool_call["function"]["arguments"],
                    name=tool_call["function"]["name"],
                )
                tool_call_object = ChatCompletionMessageToolCallParam(
                    id=tool_call["id"], function=function, type=tool_call["type"]
                )
                tool_calls.append(tool_call_object)

            # handle function calls and switching agents
            partial_response = await active_agent.handle_tool_calls(tool_calls)
            memory.extend(partial_response.messages)
            if partial_response.agent:
                active_agent = partial_response.agent

        yield {
            "response": Response(
                value=active_agent.get_value(memory[-1]["content"]),
                messages=memory[init_len:],
                agent=active_agent,
            )
        }


    def _get_user_message(self, inputs: tuple) -> dict:
        def user_message_part(input):
            if isinstance(input, str):
                return {
                    "type": "text",
                    "text": input,
                }
            elif isinstance(input, dict):
                return input
            elif hasattr(input, 'read'):  # is file-like object
                mime_type = get_mime_type_from_file_like_object(input)
                content = input.read()
                base64_content = base64.b64encode(content).decode('utf-8')
                return {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_content}",
                    },
                }
            else:
                raise ValueError(f"Unsupported prompt element type: {type(input)}")

        if len(inputs) == 1 and isinstance(inputs[0], str):
            # Keep it simple if there's only one string input
            return {"role": "user", "content": inputs[0]}
        else:
            return {"role": "user", "content": [user_message_part(input) for input in inputs]} 
        

    async def run(
            self,
            *inputs,
            stream: Optional[bool] = False,
            max_turns: Optional[int] = float("inf"),
            execute_tools: Optional[bool] = True,
    ) -> Response:
        memory = self.memory
        if inputs:
            memory.append(self._get_user_message(inputs))

        if stream:
            return self._run_and_stream(
                max_turns=max_turns,
                execute_tools=execute_tools,
            )
        
        init_len = len(memory)
        active_agent = self
        self.logger.info("Starting run with prompt: %s", inputs)

        while len(memory) - init_len < max_turns and active_agent:
            active_agent.logger.info("Getting completion...")
            active_agent._before_chat_completion()
            # get completion with current history, agent
            completion = await active_agent.get_chat_completion()
            message = completion.choices[0].message
            if active_agent.logger.level == logging.DEBUG:
                active_agent.logger.debug("Received completion: %s", message)
            else:
                active_agent.logger.info("Received completion.")
            message.sender = active_agent.name

            if not message.tool_calls or not execute_tools:
                memory.append(message.model_dump())
                break

            # handle function calls and switching agents
            partial_response = await active_agent.handle_tool_calls(message.tool_calls)
            if partial_response.filtered_tool_calls:
                # Only add tool calls to memory if there are any left after filtering
                memory.append(message.model_dump())
            memory.extend(partial_response.messages)
            if partial_response.result:
                active_agent.logger.debug("Final answer reached in tool call. Ending turn.")
                return Response(
                    value=partial_response.result.value,
                    messages=memory[init_len:],
                    agent=active_agent,
                )
            if partial_response.agent:
                active_agent = partial_response.agent
                active_agent.memory = memory

        active_agent.logger.debug("Run completed")
        return Response(
            value=self.get_value(memory[-1]["content"]),
            messages=memory[init_len:],
            agent=active_agent,
        )
    

    def run_sync(
            self, 
            *inputs,
            stream: bool = False, 
            max_turns: int = float("inf"), 
            execute_tools: bool = True
    ) -> Response:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.run(*inputs, stream=stream, max_turns=max_turns, execute_tools=execute_tools))

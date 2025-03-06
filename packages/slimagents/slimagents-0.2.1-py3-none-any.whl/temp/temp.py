import asyncio
from dataclasses import dataclass
import json
import logging
from typing import List
from slimagents import Agent, run_demo_loop

from pydantic import BaseModel, Field

from slimagents.util import type_to_response_format

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create logger for this module
logger = logging.getLogger(__name__)

class Weather(BaseModel):
    location: str
    description: str

class WeatherAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Weather Agent", 
            instructions="""You are a weather agent. 
You will always answer questions about the weather using the provided tools. 
For non weather questions, you will transfer the conversation to the triage agent.""",
            tools=[self.get_weather],
            response_format=Weather
        )
        self.current_weather = "sunny"

    def get_weather(self, location: str) -> str:
        ret = self.current_weather
        if self.current_weather == "sunny":
            self.current_weather = "rainy"
        else:
            self.current_weather = "sunny"
        return ret

weather_agent = WeatherAgent()

def transfer_to_weather_agent():
    return weather_agent


class ShoppingListItem(BaseModel):
    item: str
    quantity: int = Field(default=1, description="The quantity of the item to add to the shopping list.")

class ShoppingList(BaseModel):
    elements: List[ShoppingListItem]

shopping_list_agent = Agent(
    name="Shopping List Agent",
    instructions="You are a shopping list agent. You report the current shopping list.",
    response_format=ShoppingList
)

def send_to_shopping_list_agent():
    return shopping_list_agent


@dataclass
class ShoppingList:
    elements: List[ShoppingListItem]

triage_agent = Agent(
    name="Triage Agent",
    instructions="""Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent. 
If there is no special purpose agent availble, then answer the question yourself.""",
    tools=[transfer_to_weather_agent, send_to_shopping_list_agent],
)

def transfer_back_to_triage_agent():
    return triage_agent

weather_agent.tools.append(transfer_back_to_triage_agent)

triage_agent.logger.setLevel(logging.DEBUG)
# run_demo_loop(triage_agent, stream=True)

# print(asyncio.run(weather_agent.run("What is the weather in San Francisco?")))
# print(asyncio.run(shopping_list_agent.run("Add milk to shopping list."))

# print(type_to_response_format(Weather))
# print(json.dumps(type_to_response_format(ShoppingList), indent=4))
# print(type_to_response_format(ShoppingList))

class SubCalculation(BaseModel):
    expression: str = Field(description="The expression of the sub calculation.")
    result: float = Field(description="The result of the sub calculation.")

class Result(BaseModel):
    sub_calculations: List[SubCalculation] = Field(description="Any sub calculations necessary to answer the question.")
    result: float = Field(description="The final result of the math question.")

test_agent = Agent(
    name="Test Agent",
    instructions="Your are a great poet",
    response_format=Result,
    # model="gemini/gemini-1.5-flash-002"
)


# {}.pop("bla", None)
# print(["a", "b", "c"] == ["a", "b", "c", "d"])

print(test_agent.run_sync("What is 1+5 * 4-4 / 2?").value)
# test_agent.temperature = 2
# test_agent.temperature = 0
# test_agent.extra_llm_params = {"modalities": ["text", "audio"]}
# test_agent.max_completion_tokens = 20
test_agent.logger.setLevel(logging.DEBUG)
# print(asyncio.run(test_agent.run("Write a very short poem about the future of AI")).value)
# print(asyncio.run(Agent().run()).value)



# class Test(BaseModel):
#     @property
#     def test(self):
#         return "test"
    
# class SubTest(Test):
#     def test(self):
#         return "subtest"

# print(SubTest().test)
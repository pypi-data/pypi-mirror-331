import json
from typing import List, Dict, Any, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from linearagent.memory import Memory
from linearagent.tool import ToolLibrary, basic_tools


# --------------------------------
class PlanStep(BaseModel):
    """
    Represents a single step in a plan. This step designates which tool to use
    and the prompt or command to provide to that tool.
    """

    tool_name: str = Field(..., description="Name of the tool to be used in this step.")
    input: list[str] = Field(
        ...,
        description=(
            "A list of memory keys to provide input to the tool."
            "These keys should be present in memory."
            "The tool will use the values stored under these keys as input."
            "The order of the keys should match the order of the tool's input parameters."
            "'thread' and 'all' are special keys that can send the thread or the entire memory to the tool."
        ),
    )
    output: list[str] = Field(
        ...,
        description=(
            "A dictionary of memory keys, along with it's description."
            "The tool will store the values under these keys in memory."
            "These keys may or may not exist in the memory, a key with the same name with replace the existing value in the memory."
        ),
    )


class Plan(BaseModel):
    """
    Represents a collection of steps (PlanStep). Each PlanStep indicates
    an action or instruction to be performed, typically mapped to a tool.
    """

    steps: List[PlanStep] = Field(
        ...,
        description=(
            "A list of steps (PlanStep) that comprise the plan."
            "Each step represents a tool execution from the tool library."
            "These tools are linked with each other via the memory keys."
            "Set appropriate memory keys in the input and output fields to link the tools."
        ),
    )
    initial_memory: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional dictionary of initial memory keys and values to set before executing the plan."
            "These values will be populated in memory before any steps are executed."
            "Use this to set values that are needed by the first steps in the plan."
        ),
    )


# --------------------------------
# LinearAgent that:
#   1) Creates an initial plan (tool_name + prompt).
#   2) For each tool call, uses an LLM to produce structured parameters.
#   3) Executes the tool with validated parameters.
# --------------------------------
class LinearAgent:
    def __init__(
        self,
        developer_instructions: str,
        tool_library: ToolLibrary,
        planner_model: str = "gpt-4o-2024-08-06",
        planner_temperature: float = 0.0,
    ):
        self.memory = Memory()
        self.tool_library = tool_library

        self.planner_message = (
            "You are a planning assistant for an Agent. The user wants a plan to "
            "accomplish the given query. Produce a JSON array of steps, where each "
            "step is an object with the keys: 'tool_name', 'input' (list of memory keys), "
            "and 'output' (list of memory keys)."
        )
        self.planner_message += "Developer Instructions: " + developer_instructions

        self.planner_message += self.tool_library.stringify()

        self.plan = None
        self.client = OpenAI()
        self.planner_temperature = planner_temperature
        self.planner_model = planner_model

    def make_plan(self, thread) -> list:
        """
        Calls the LLM to produce a plan in a minimal schema:
        - tool_name (str)
        - input (list[str])
        - output (list[str])

        Returns:
            list: A list of plan steps. Each step is a dict:
                {
                    "tool_name": <str>,
                    "input": [<str>, ...],
                    "output": [<str>, ...]
                }
        """

        self.memory.map_thread(thread)

        # Prepare the messages to send to the LLM
        messages = [
            {"role": "system", "content": (self.planner_message)},
        ]
        for message in self.memory.get("thread"):
            messages.append(message)

        # Add memory to the last message
        messages[-1]["content"] += self.memory.stringify()

        # Debug: Print the messages
        print(json.dumps(messages, indent=2))

        # Call the same helper function that invokes the OpenAI API
        response = self._get_llm_response(
            messages,
            response_format=Plan,
            model=self.planner_model,
            temperature=self.planner_temperature,
        )

        # The response content should be valid JSON representing a list of steps.
        plan = json.loads(response.choices[0].message.content)

        # Return the list as Python objects (list of dicts).
        return plan

    def execute_plan(self, plan: list):
        # Set initial memory values if provided
        if plan.get("initial_memory"):
            for key, value in plan["initial_memory"].items():
                self.memory.set(key, value)
                
        for step_num, step in enumerate(plan["steps"], start=1):
            tool_name = step["tool_name"]
            tool = self.tool_library.get(tool_name)
            if tool is None:
                raise ValueError(f"Tool '{tool_name}' is not registered.")

            # Validate the input keys
            if not set(step["input"]).issubset(self.memory.keys()):
                missing_keys = set(step["input"]) - set(self.memory.keys())
                raise ValueError(f"Step {step_num}: Missing input keys: {missing_keys}")

            # Prepare the input and output parameters
            input = [self.memory.get(key) for key in step["input"]]

            # Setup Tool
            tool.setup(input)

            # Execute the tool
            tool.execute()

            # Store the output in memory as per the step's output keys using values from tool.poll()
            for key, value in zip(step["output"], tool.poll()):
                self.memory.set(key, value)

    def _get_llm_response(
        self, messages, response_format=None, model="gpt-4o", temperature=0
    ):
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=temperature,
        )
        return response


# --------------------------------
# Usage Example
# --------------------------------
if __name__ == "__main__":
    # Initialize the Tool Library
    tool_library = ToolLibrary()
    tool_library.register(basic_tools)

    # Initialize the LinearAgent
    agent = LinearAgent(
        developer_instructions="Develop a plan to accomplish the given query.",
        tool_library=tool_library,
        planner_model="gpt-4o",
        planner_temperature=0.0,
    )

    # Define a thread with a query
    thread = [
        {
            "role": "user",
            "content": "For 5 times, take input from user and echo it to console.",
        },
    ]

    agent.memory.set("introduction", "This is a simple echo program.")

    # Generate a plan
    plan = agent.make_plan(thread)

    # Execute the plan
    agent.execute_plan(plan)

    # Print the memory
    print(agent.memory.stringify())

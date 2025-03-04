import builtins
import json


class Tool:
    """
    Base class for all tools.
    Each tool must define:
      - A `name`.
      - A `tool_message` describing the prompt to send to the LLM for parameter generation.
      - A dictionary `tool_inputs` describing input parameters for these tools.
      - A dictionary `tool_` describing outputs given by the tool.
      - An `execute()` method that takes in memory and validated parameters.
    """

    def __init__(
        self,
        name: str,
        tool_message: str,
        tool_inputs: dict = None,
        tool_returns: dict = None,
    ):
        """
        Initialize a new Tool instance.

        Args:
            name (str): The name of the tool.
            tool_message (str): The prompt to send to the LLM for parameter generation.
            tool_inputs (dict, optional): Description of input parameters for the tool.
            tool_returns (dict, optional): Description of output parameters for the tool.
        """
        self.name = name
        self.tool_message = tool_message
        self.tool_inputs = tool_inputs if tool_inputs is not None else {}
        self.tool_returns = tool_returns if tool_returns is not None else {}

    def setup(self, inputs: list):
        """
        Maps an ordered list of input values to instance variables based on tool_inputs.
        Also creates instance variables for each tool_returns key, initialized to None.

        Args:
            inputs (list): The inputs to set up the tool with (in order).
        """

        # Ensure we have the correct number of inputs
        if len(inputs) != len(self.tool_inputs):
            raise ValueError(
                f"Expected {len(self.tool_inputs)} inputs, but got {len(inputs)}."
            )

        # Ensure that the input types are as expected
        type_mapping = {
            "int": int,
            "str": str,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
        }
        for i, (input_key, input_value) in enumerate(self.tool_inputs.items()):
            if not isinstance(inputs[i], type_mapping.get(input_value["Type"])):
                raise TypeError(
                    f"Expected input {input_key} to be of type {input_value['Type']}, but got {type(inputs[i])}."
                )

        # Map each input to an instance variable named after its key in tool_inputs
        i = 0
        for input_key in self.tool_inputs.keys():
            setattr(self, input_key, inputs[i])
            i += 1

        # Initialize outputs to None for each key in tool_returns
        for output_key in self.tool_returns.keys():
            setattr(self, output_key, None)

    def poll(self):
        """
        Returns a list of output values based on the keys in tool_returns.
        The order corresponds to the order of keys in tool_returns.

        Returns:
            list: A list of output values for each key in tool_returns.
        """
        return [getattr(self, output_key) for output_key in self.tool_returns.keys()]

    def execute(self):
        """
        Subclasses should implement custom logic here.
        """
        raise NotImplementedError("Subclasses must implement 'execute'.")


class ToolLibrary:
    """
    A library of tools that can be used to perform various tasks.
    """

    def __init__(self):
        self.tools = {}

    def register(self, tools: list):
        """
        Register a new tool with the library.
        Args:
            tool: The tool to register.
        """
        for tool in tools:
            if tool.name in self.tools:
                raise ValueError(f"Tool '{tool.name}' is already registered.")
            self.tools[tool.name] = tool

    def get(self, name: str):
        """
        Retrieve a tool by name.
        Args:
            name (str): The name of the tool to retrieve.
        Returns:
            Tool: The tool instance.
        """
        return self.tools.get(name)

    def list(self) -> list:
        """
        List all available tools.
        Returns:
            list: A list of tool names.
        """
        return list(self.tools.keys())

    def stringify(self) -> str:
        """
        Stringify the tool library.
        Returns:
            str: A string representation of the tool library.
        """
        lines = []
        lines.append("# --------------------------------")
        lines.append("Tool Library")
        lines.append("# --------------------------------")
        lines.append("")

        for _, tool in self.tools.items():
            lines.append(f"Name: {tool.name}")
            lines.append(f"Message: {tool.tool_message}")

            # Use json.dumps for inputs
            lines.append("Inputs:")
            lines.append(json.dumps(tool.tool_inputs, indent=4))
            lines.append("")

            # Use json.dumps for outputs
            lines.append("Returns: (set your own memory keys)")
            lines.append(json.dumps(tool.tool_returns, indent=4))
            lines.append("")

        return "\n".join(lines)


# --------------------------------
# Basic Tools
# --------------------------------


class ConsoleInput(Tool):
    def __init__(self):
        super().__init__(
            name="console_input",
            tool_message="Reads input from the console.",
            tool_inputs={},
            tool_returns={
                "user_response": {
                    "Description": "Store the user response.",
                    "Type": "str",
                }
            },
        )

    def execute(self):
        prompt_str = getattr(self, "prompt", "")
        # Capture user input in the user_response attribute
        self.user_response = builtins.input(prompt_str)


class ConsoleOutput(Tool):
    def __init__(self):
        super().__init__(
            name="console_output",
            tool_message="Prints output to the console.",
            tool_inputs={
                "output": {
                    "Description": "The output to print to the console.",
                    "Type": "str",
                }
            },
            tool_returns={},
        )

    def execute(self):
        print(self.output)


basic_tools = [ConsoleInput(), ConsoleOutput()]

from smolagents.tools import Tool
from smolagents._function_type_hints_utils import (
    _parse_google_format_docstring,
    DocstringParsingException,
    get_type_hints,
    _parse_type_hint,
    TypeHintParsingException,
)
from typing import Callable, Dict
import inspect
import importlib

import re
import json


# from smolagents._function_type_hints_utils
# modified to ignore self parameter
def _convert_type_hints_to_json_schema(
    func: Callable, error_on_missing_type_hints: bool = True
) -> Dict:
    type_hints = get_type_hints(func)
    signature = inspect.signature(func)

    properties = {}
    for param_name, param_type in type_hints.items():
        properties[param_name] = _parse_type_hint(param_type)

    required = []
    for param_name, param in signature.parameters.items():
        if param_name == "self":
            continue
        if param.annotation == inspect.Parameter.empty and error_on_missing_type_hints:
            raise TypeHintParsingException(
                f"Argument {param.name} is missing a type hint in function {func.__name__}"
            )
        if param_name not in properties:
            properties[param_name] = {}

        if param.default == inspect.Parameter.empty:
            required.append(param_name)
        else:
            properties[param_name]["nullable"] = True

    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required

    return schema


# from smolagents._function_type_hints_utils
# modified to ignore self parameter
def get_json_schema(func: Callable) -> Dict:
    """
    This function generates a JSON schema for a given function, based on its docstring and type hints. This is
    mostly used for passing lists of tools to a chat template. The JSON schema contains the name and description of
    the function, as well as the names, types and descriptions for each of its arguments. `get_json_schema()` requires
    that the function has a docstring, and that each argument has a description in the docstring, in the standard
    Google docstring format shown below. It also requires that all the function arguments have a valid Python type hint.

    Although it is not required, a `Returns` block can also be added, which will be included in the schema. This is
    optional because most chat templates ignore the return value of the function.

    Args:
        func: The function to generate a JSON schema for.

    Returns:
        A dictionary containing the JSON schema for the function.

    Examples:
    ```python
    >>> def multiply(x: float, y: float):
    >>>    '''
    >>>    A function that multiplies two numbers
    >>>
    >>>    Args:
    >>>        x: The first number to multiply
    >>>        y: The second number to multiply
    >>>    '''
    >>>    return x * y
    >>>
    >>> print(get_json_schema(multiply))
    {
        "name": "multiply",
        "description": "A function that multiplies two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "The first number to multiply"},
                "y": {"type": "number", "description": "The second number to multiply"}
            },
            "required": ["x", "y"]
        }
    }
    ```

    The general use for these schemas is that they are used to generate tool descriptions for chat templates that
    support them, like so:

    ```python
    >>> from transformers import AutoTokenizer
    >>> from transformers.utils import get_json_schema
    >>>
    >>> def multiply(x: float, y: float):
    >>>    '''
    >>>    A function that multiplies two numbers
    >>>
    >>>    Args:
    >>>        x: The first number to multiply
    >>>        y: The second number to multiply
    >>>    return x * y
    >>>    '''
    >>>
    >>> multiply_schema = get_json_schema(multiply)
    >>> tokenizer = AutoTokenizer.from_pretrained("CohereForAI/c4ai-command-r-v01")
    >>> messages = [{"role": "user", "content": "What is 179 x 4571?"}]
    >>> formatted_chat = tokenizer.apply_chat_template(
    >>>     messages,
    >>>     tools=[multiply_schema],
    >>>     chat_template="tool_use",
    >>>     return_dict=True,
    >>>     return_tensors="pt",
    >>>     add_generation_prompt=True
    >>> )
    >>> # The formatted chat can now be passed to model.generate()
    ```

    Each argument description can also have an optional `(choices: ...)` block at the end, such as
    `(choices: ["tea", "coffee"])`, which will be parsed into an `enum` field in the schema. Note that this will
    only be parsed correctly if it is at the end of the line:

    ```python
    >>> def drink_beverage(beverage: str):
    >>>    '''
    >>>    A function that drinks a beverage
    >>>
    >>>    Args:
    >>>        beverage: The beverage to drink (choices: ["tea", "coffee"])
    >>>    '''
    >>>    pass
    >>>
    >>> print(get_json_schema(drink_beverage))
    ```
    {
        'name': 'drink_beverage',
        'description': 'A function that drinks a beverage',
        'parameters': {
            'type': 'object',
            'properties': {
                'beverage': {
                    'type': 'string',
                    'enum': ['tea', 'coffee'],
                    'description': 'The beverage to drink'
                    }
                },
            'required': ['beverage']
        }
    }
    """
    doc = inspect.getdoc(func)
    if not doc:
        raise DocstringParsingException(
            f"Cannot generate JSON schema for {func.__name__} because it has no docstring!"
        )
    doc = doc.strip()
    main_doc, param_descriptions, return_doc = _parse_google_format_docstring(doc)

    json_schema = _convert_type_hints_to_json_schema(func)
    if (return_dict := json_schema["properties"].pop("return", None)) is not None:
        if (
            return_doc is not None
        ):  # We allow a missing return docstring since most templates ignore it
            return_dict["description"] = return_doc
    else:
        return_dict = {}
    for arg, schema in json_schema["properties"].items():
        if "arg" == "self":
            continue
        if arg not in param_descriptions:
            raise DocstringParsingException(
                f"Cannot generate JSON schema for {func.__name__} because the docstring has no description for the argument '{arg}'"
            )
        desc = param_descriptions[arg]
        enum_choices = re.search(r"\(choices:\s*(.*?)\)\s*$", desc, flags=re.IGNORECASE)
        if enum_choices:
            schema["enum"] = [c.strip() for c in json.loads(enum_choices.group(1))]
            desc = enum_choices.string[: enum_choices.start()].strip()
        schema["description"] = desc

    return (
        main_doc,
        json_schema["properties"],
        return_dict.get("description", "") or "null",
    )


def load_tools(tools_file):

    # Load module from file path
    spec = importlib.util.spec_from_file_location("tools", tools_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tool_classes = {}

    # Find and instantiate the Tool class
    for item_name in dir(module):
        item = getattr(module, item_name)
        if isinstance(item, type) and issubclass(item, Tool) and item != Tool:
            tool_classes[item.name] = item

    return tool_classes


def get_tool(tools, name, *args, **kwargs):
    if name in tools:
        return tools[name](*args, **kwargs)
    else:
        raise Exception(f"Tool not found: {name} not in {', '.join(tools.keys())}")

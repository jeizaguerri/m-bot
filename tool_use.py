import importlib.util
import sys
import json
import os

DEFAULT_TOOL_DESCRIPTIONS_FILE = "tools/default_tool_descriptions.json"
GENERATED_TOOL_DESCRIPTIONS_FILE = "tools/generated_tool_descriptions.json"
default_tool_descriptions = []
generated_tool_descriptions = []


def load_tool_descriptions():
    # Default tools
    if not os.path.exists(DEFAULT_TOOL_DESCRIPTIONS_FILE):
        raise FileNotFoundError(f"Default tool descriptions file not found at {DEFAULT_TOOL_DESCRIPTIONS_FILE}")

    with open(DEFAULT_TOOL_DESCRIPTIONS_FILE, "r") as file:
        descriptions = json.load(file)
        for tool in descriptions:
            default_tool_descriptions.append(tool["description"])

    # Generated tools
    if os.path.exists(GENERATED_TOOL_DESCRIPTIONS_FILE):
        with open(GENERATED_TOOL_DESCRIPTIONS_FILE, "r") as file:
            descriptions = json.load(file)
            for tool in descriptions:
                generated_tool_descriptions.append(tool["description"])
    else:
        with open(GENERATED_TOOL_DESCRIPTIONS_FILE, "w") as file:
            json.dump([], file)

def save_tool_description(name, description):
    # In memory
    generated_tool_descriptions.append(description)

    # Persistent
    with open(GENERATED_TOOL_DESCRIPTIONS_FILE, "r") as file:
        descriptions = json.load(file)
        if not any(tool["name"] == name for tool in descriptions):
            descriptions.append({
                "name": name,
                "description": description
            })
        else:
            raise ValueError(f"Tool with name {name} already exists")
    
    with open(GENERATED_TOOL_DESCRIPTIONS_FILE, "w") as file:
        json.dump(descriptions, file)


def import_and_execute(file_path, function_name, function_inputs):
    module_name = file_path.replace("/", "_").replace(".", "_")  # Unique module name

    # Load the module from file
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Call the specified function
    if hasattr(module, function_name):
        func = getattr(module, function_name)
        if callable(func):
            return func(*function_inputs)  # Execute function
        else:
            raise TypeError(f"'{function_name}' is not a callable function")
    else:
        raise AttributeError(f"Function '{function_name}' not found in {file_path}")
    
def get_tool_descriptions():
    return default_tool_descriptions + generated_tool_descriptions
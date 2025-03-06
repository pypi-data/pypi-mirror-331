import os
import inspect
import json
from typing import List, Dict, Any
def collect_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Collects all the json schemas from the folder and creates the final schema dictonary.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing all the schemas. 
    """
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])
    if caller_module is None or not hasattr(caller_module, '__file__'):
        raise RuntimeError("Unable to determine caller module's directory.")
    caller_dir = os.path.dirname(os.path.abspath(caller_module.__file__))
    schemas = {}
    for file in os.listdir(caller_dir):
        # print(f"Collecting from {caller_dir}/{file}")
        if file.endswith('.json'):
            with open(os.path.join(caller_dir, file), "r") as f:
                schemas[file.replace('.json', '')] = json.load(f)
    return schemas

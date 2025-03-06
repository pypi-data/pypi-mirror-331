import os
import importlib
import pkgutil
import inspect


def collect_tasks(prefix="task_"):
    """
    Dynamically loads all tasks matching a given prefix from the caller's package.

    Args:
        prefix (str): The prefix of the module names to load (default: "task_").

    Returns:
        list: A list of dictionaries extracted from the discovered modules. Each task module will have only one dictionary
            for better organization of the task files.
    """
    tasks = []

    # Determine the caller module to get the correct package and path
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])

    if not caller_module or not hasattr(caller_module, "__package__"):
        raise RuntimeError("Unable to determine the caller package.")

    package_name = caller_module.__package__
    module_path = os.path.dirname(os.path.abspath(caller_module.__file__))

    # Discover modules in the same package as the caller
    for _, module_name, _ in pkgutil.iter_modules([module_path]):
        if module_name.startswith(prefix):
            try:
                module = importlib.import_module(f"{package_name}.{module_name}")
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, dict):  # Collect only dictionary objects
                        tasks.append(obj)
            except Exception as e:
                print(f"Failed to import {module_name}: {e}")

    return tasks

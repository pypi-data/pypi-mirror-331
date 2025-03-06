# Copyright 2025 Karta

from typing import List, Dict, Any
from karta_benchmarks.general_helpers.collect_tasks import collect_tasks


def factory() -> List[Dict[str, Any]]:
    """
    Factory function to create a task factory.

    Returns:
        List[Dict[str, Any]]: A list of tasks and their details
    """
    return collect_tasks()

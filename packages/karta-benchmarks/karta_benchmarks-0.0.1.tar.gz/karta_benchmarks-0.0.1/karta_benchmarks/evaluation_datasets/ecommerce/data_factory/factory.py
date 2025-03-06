# Copyright 2025 Karta

import os
import json
import karta_benchmarks.evaluation_datasets.ecommerce.raw_data as raw_data
from typing import Dict, Any

def factory() -> Dict[str, Dict]:
    """
    This function loads all the json files in the raw_data directory and 
    returns a dictionary of the data. This is the base data set that will 
    be used in the evaluations. In this case the data is present in the raw_data directory
    in the domain level package. All the json files in the directory are loaded

    Returns:
        Dict[str, Dict]: A dictionary of the data. The keys are the file names (without the .json extension)
            and the values are the data.
    """
    json_files = [f for f in os.listdir(raw_data.__path__[0]) if f.endswith('.json')]
    json_data = {}
    for file in json_files:
        with open(os.path.join(raw_data.__path__[0], file), 'r') as f:
            json_data[file.replace('.json', '')] = json.load(f)
    return json_data
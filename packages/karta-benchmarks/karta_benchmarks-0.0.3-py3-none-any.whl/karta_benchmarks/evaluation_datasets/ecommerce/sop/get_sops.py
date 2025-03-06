from typing import Dict, Any
import os

def sops() -> Dict[str, Any]:
    """
    Get the SOPs for the ecommerce domain.

    Returns:
        List[Dict[str, Any]]: A list of SOPs and their details
    """
    sops = {}

    # Get the SOPs from the sop directory
    # Only the md files are considered as SOPs
    # Creates a dictionary with the file name (minus the extension) as the key and the file content as the value
    for file in os.listdir("karta_benchmarks/evaluation_datasets/ecommerce/sop"):
        if file.endswith(".md"):
            with open(os.path.join("karta_benchmarks/evaluation_datasets/ecommerce/sop", file), "r") as f:
                sops[file.split(".")[0]] = f.read()
    return sops
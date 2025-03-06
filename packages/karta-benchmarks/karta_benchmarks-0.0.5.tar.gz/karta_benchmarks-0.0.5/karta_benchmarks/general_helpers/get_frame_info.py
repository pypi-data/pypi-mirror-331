import inspect
from typing import Dict, Any
def get_frame_info(frame: inspect.FrameInfo) -> Dict[str, Any]:
    """
    Get the frame information of the current function.
    """
    function_name = inspect.getframeinfo(frame).function
    args, _, _, values = inspect.getargvalues(frame)
    
    return {
        "function_name": function_name,
        "arguments": {
            arg: values[arg] for arg in args
        }
    }
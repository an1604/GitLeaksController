import json

from pydantic import BaseModel
from typing import Optional


class LeakReport(BaseModel):
    filename: str
    line_range: str
    description: Optional[str]

def log_error_to_file(exit_code, error_message, error_file="error.json"):
    """log structured error to a JSON file (bonus section)"""
    error_data = {
        "exit_code": exit_code,
        "error_message": error_message
    }
    with open(error_file, "w") as f:
        json.dump(error_data, f, indent=4)
    print(f"Error logged to {error_file}")
    print(error_data)
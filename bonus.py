from pydantic import BaseModel
from typing import Optional


class LeakReport(BaseModel):
    filename: str
    line_range: str
    description: Optional[str]


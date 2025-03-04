from typing import Optional
from pydantic import BaseModel

class Error(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    stack: Optional[str] = None

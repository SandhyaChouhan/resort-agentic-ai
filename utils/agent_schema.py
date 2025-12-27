from pydantic import BaseModel
from typing import List, Optional

class AgentDecision(BaseModel):
    agent: str
    action: str
    items: Optional[List[str]] = None
    request_type: Optional[str] = None

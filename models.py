from pydantic import BaseModel
from typing import List,Optional


class Survey(BaseModel):
    id: Optional[str] = None  # Add this line to allow custom ID
    title :str
    description :str
    questions :List[str]
    created_at :Optional[str] = None

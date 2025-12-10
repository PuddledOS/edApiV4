from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MainRootResponse(BaseModel):
    message: str
    version: str
    language: str
    docs: str
    status: str

class MainStatusResponse(BaseModel):
    health: str

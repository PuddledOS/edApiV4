from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ExportTaskResponse(BaseModel):
    """Response for export task initiation."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None

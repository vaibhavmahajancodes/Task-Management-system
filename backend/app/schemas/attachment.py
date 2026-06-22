from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserSummary


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    file_size: int
    content_type: Optional[str] = None
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    uploaded_by: int
    uploader: UserSummary
    created_at: datetime
    download_url: str = ""

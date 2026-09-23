from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    instrument_id: Optional[str] = None
    test_code: Optional[str] = None
    file_name: str
    file_type: str
    file_size: int
    file_hash: str
    title: str
    description: Optional[str] = None
    uploaded_by_id: Optional[str] = None
    created_at: datetime

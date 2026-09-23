from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class StandardRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_id: str
    clause: str
    test_id: str
    description: str
    formula: Optional[str] = None
    inputs: List[Any] = []
    unit: str
    limits: Dict[str, Any] = {}
    conditions: Dict[str, Any] = {}
    applicability: str
    pass_fail_logic: str
    source_reference: str
    verification_status: str
    notes: Optional[str] = None
    is_active: bool

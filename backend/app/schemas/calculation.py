from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models import TestStatusEnum

class RunCalculationRequest(BaseModel):
    session_id: str
    test_codes: Optional[List[str]] = None

class CalculationResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    test_code: str
    rule_id: Optional[str] = None
    clause: str
    formula: str
    input_values: Dict[str, Any]
    calculated_value: float
    permissible_value: float
    margin: float
    unit: str
    status: TestStatusEnum
    calculation_timestamp: datetime

class ComplianceResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    test_code: str
    test_name: str
    clause: str
    standard_reference: str
    observed_summary: str
    permissible_summary: str
    status: TestStatusEnum
    basis: str
    explainability_json: Dict[str, Any]
    created_at: datetime

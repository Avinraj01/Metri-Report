from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models import ReportStatusEnum, TestStatusEnum

class ObservationInput(BaseModel):
    test_code: str
    point_name: str
    test_load: float = Field(..., ge=0)
    observed_indication: float = Field(..., ge=0)
    delta_load: float = Field(0.0, ge=0)
    remarks: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

class ObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    test_code: str
    point_name: str
    test_load: float
    observed_indication: float
    delta_load: float
    calculated_error: Optional[float] = None
    corrected_error: Optional[float] = None
    mpe: Optional[float] = None
    status: TestStatusEnum
    remarks: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime

class TestSessionCreate(BaseModel):
    instrument_id: str
    session_name: str
    ambient_temp: float = 22.0
    ambient_humidity: float = 55.0
    ambient_pressure: float = 1013.25
    ambient_voltage: float = 230.0
    notes: Optional[str] = None

class TestSessionUpdateConditions(BaseModel):
    ambient_temp: float
    ambient_humidity: float
    ambient_pressure: float
    ambient_voltage: float
    notes: Optional[str] = None

class TestSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_number: str
    instrument_id: str
    session_name: str
    status: ReportStatusEnum
    overall_compliance: TestStatusEnum
    ambient_temp: float
    ambient_humidity: float
    ambient_pressure: float
    ambient_voltage: float
    test_engineer_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    approver_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

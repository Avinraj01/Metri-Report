from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator, ConfigDict
from app.models import AccuracyClassEnum

class InstrumentBase(BaseModel):
    instrument_name: str = Field(..., min_length=2, max_length=255)
    model: str = Field(..., min_length=1, max_length=255)
    instrument_type: str = Field(..., min_length=2, max_length=255)
    serial_number: str = Field(..., min_length=1, max_length=255)
    manufacturer: str = Field(..., min_length=2, max_length=255)
    manufacturer_address: Optional[str] = None
    applicant_name: str = Field(..., min_length=2, max_length=255)
    applicant_address: Optional[str] = None
    
    accuracy_class: AccuracyClassEnum = AccuracyClassEnum.CLASS_III
    max_capacity: float = Field(..., gt=0, description="Max capacity in designated unit")
    min_capacity: float = Field(..., gt=0, description="Min capacity in designated unit")
    e_value: float = Field(..., gt=0, description="Verification scale interval e")
    d_value: float = Field(..., gt=0, description="Actual scale interval d")
    unit: str = Field("kg", min_length=1, max_length=20)
    
    num_ranges: int = Field(1, ge=1, le=5)
    is_multi_range: bool = False
    is_multi_interval: bool = False
    is_electronic: bool = True
    is_self_indicating: bool = True
    is_mobile: bool = False
    is_portable: bool = False
    is_weighbridge: bool = False
    
    load_receptor_type: str = "Platform"
    num_support_points: int = Field(4, ge=1, le=32)
    load_cell_details: Optional[str] = None
    indicator_details: Optional[str] = None
    software_version: Optional[str] = None
    firmware_id: Optional[str] = None
    power_supply: str = "230 V AC, 50 Hz"
    
    temp_min: float = -10.0
    temp_max: float = 40.0
    humidity_min: float = 20.0
    humidity_max: float = 85.0
    voltage_nominal: float = 230.0
    voltage_min: float = 195.5
    voltage_max: float = 253.0
    
    country_of_manufacture: str = "India"
    application_use: str = "Commercial Trade / Industrial Weighing"
    laboratory: str = "National Legal Metrology Testing Centre, New Delhi"

    @model_validator(mode="after")
    def validate_metrology(self):
        if self.max_capacity <= self.min_capacity:
            raise ValueError("Max capacity must be strictly greater than Min capacity.")
        if self.d_value > self.e_value:
            raise ValueError("Actual scale interval d cannot be greater than verification scale interval e (OIML R 76-1 Cl. 3.1.2).")
        if self.temp_min >= self.temp_max:
            raise ValueError("Operating temperature temp_min must be less than temp_max.")
        if self.voltage_min >= self.voltage_max:
            raise ValueError("Voltage range voltage_min must be less than voltage_max.")
        return self

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentUpdate(BaseModel):
    instrument_name: Optional[str] = None
    model: Optional[str] = None
    instrument_type: Optional[str] = None
    manufacturer: Optional[str] = None
    manufacturer_address: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    accuracy_class: Optional[AccuracyClassEnum] = None
    max_capacity: Optional[float] = Field(None, gt=0)
    min_capacity: Optional[float] = Field(None, gt=0)
    e_value: Optional[float] = Field(None, gt=0)
    d_value: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    load_cell_details: Optional[str] = None
    indicator_details: Optional[str] = None
    software_version: Optional[str] = None
    firmware_id: Optional[str] = None
    status: Optional[str] = None

class InstrumentResponse(InstrumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    n_intervals: int
    status: str
    created_at: datetime
    updated_at: datetime

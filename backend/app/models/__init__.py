import enum
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    LAB_MANAGER = "LAB_MANAGER"
    TEST_ENGINEER = "TEST_ENGINEER"
    REVIEWER = "REVIEWER"
    VIEWER = "VIEWER"

class AuthProviderEnum(str, enum.Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    HYBRID = "HYBRID"

class AccuracyClassEnum(str, enum.Enum):
    CLASS_I = "I"
    CLASS_II = "II"
    CLASS_III = "III"
    CLASS_IIII = "IIII"

class TestStatusEnum(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_TESTED = "NOT_TESTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BLOCKED = "BLOCKED"

class ReportStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    FINALIZED = "FINALIZED"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER, nullable=False)
    auth_provider = Column(Enum(AuthProviderEnum), default=AuthProviderEnum.LOCAL, nullable=False)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instrument_name = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    instrument_type = Column(String(255), nullable=False)  # e.g., Electronic Platform Scale, Analytical Balance
    serial_number = Column(String(255), unique=True, index=True, nullable=False)
    manufacturer = Column(String(255), nullable=False)
    manufacturer_address = Column(Text, nullable=True)
    applicant_name = Column(String(255), nullable=False)
    applicant_address = Column(Text, nullable=True)
    
    # Metrological parameters
    accuracy_class = Column(Enum(AccuracyClassEnum), nullable=False, default=AccuracyClassEnum.CLASS_III)
    max_capacity = Column(Float, nullable=False)  # Max in kg / g
    min_capacity = Column(Float, nullable=False)  # Min
    e_value = Column(Float, nullable=False)       # Verification scale interval e
    d_value = Column(Float, nullable=False)       # Actual scale division d
    n_intervals = Column(Integer, nullable=False) # n = Max / e
    unit = Column(String(20), default="kg", nullable=False)  # kg, g, mg, t
    
    num_ranges = Column(Integer, default=1)
    is_multi_range = Column(Boolean, default=False)
    is_multi_interval = Column(Boolean, default=False)
    is_electronic = Column(Boolean, default=True)
    is_self_indicating = Column(Boolean, default=True)
    is_mobile = Column(Boolean, default=False)
    is_portable = Column(Boolean, default=False)
    is_weighbridge = Column(Boolean, default=False)
    
    load_receptor_type = Column(String(255), default="Platform")
    num_support_points = Column(Integer, default=4)
    load_cell_details = Column(String(255), nullable=True)
    indicator_details = Column(String(255), nullable=True)
    software_version = Column(String(100), nullable=True)
    firmware_id = Column(String(100), nullable=True)
    power_supply = Column(String(100), default="230 V AC, 50 Hz")
    
    temp_min = Column(Float, default=-10.0)
    temp_max = Column(Float, default=40.0)
    humidity_min = Column(Float, default=20.0)
    humidity_max = Column(Float, default=85.0)
    voltage_nominal = Column(Float, default=230.0)
    voltage_min = Column(Float, default=195.5)
    voltage_max = Column(Float, default=253.0)
    
    country_of_manufacture = Column(String(100), default="India")
    application_use = Column(String(255), default="Commercial Trade / Industrial Weighing")
    date_received = Column(DateTime, default=datetime.utcnow)
    laboratory = Column(String(255), default="National Legal Metrology Testing Centre, New Delhi")
    status = Column(String(50), default="REGISTERED")  # REGISTERED, IN_TESTING, EVALUATED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_sessions = relationship("TestSession", back_populates="instrument", cascade="all, delete-orphan")
    evidence_files = relationship("Evidence", back_populates="instrument", cascade="all, delete-orphan")

class TestCatalogItem(Base):
    __tablename__ = "test_catalog"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    test_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. A.4.4.1, A.4.7, A.4.10
    test_name = Column(String(255), nullable=False)
    annex = Column(String(20), nullable=False) # Annex A, Annex B, etc.
    clause = Column(String(50), nullable=False) # e.g. A.4.4.1, 3.5.1
    category = Column(String(100), nullable=False) # Performance, Influence, Disturbance, Software
    classification = Column(String(50), default="AUTOMATED") # AUTOMATED, CONFIGURED, MANUAL_REVIEW
    applicability_condition = Column(String(255), default="ALL")
    required_inputs = Column(JSON, default=list)
    optional_inputs = Column(JSON, default=list)
    environmental_requirements = Column(String(255), nullable=True)
    procedure_summary = Column(Text, nullable=False)
    calculation_method = Column(Text, nullable=True)
    acceptance_criteria = Column(Text, nullable=False)
    evidence_required = Column(Boolean, default=False)
    source_reference = Column(String(255), default="OIML R 76-1:2006 (E)")
    is_active = Column(Boolean, default=True)

class Standard(Base):
    __tablename__ = "standards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False) # OIML R 76-1
    title = Column(String(255), nullable=False)
    organization = Column(String(100), default="OIML")
    created_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship("StandardVersion", back_populates="standard", cascade="all, delete-orphan")

class StandardVersion(Base):
    __tablename__ = "standard_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    standard_id = Column(String(36), ForeignKey("standards.id"), nullable=False)
    edition = Column(String(50), nullable=False) # 2006, 20XX
    status = Column(String(50), default="ACTIVE") # ACTIVE, DRAFT, ARCHIVED
    effective_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    standard = relationship("Standard", back_populates="versions")
    rules = relationship("StandardRule", back_populates="version_rel", cascade="all, delete-orphan")

class StandardRule(Base):
    __tablename__ = "standard_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = Column(String(36), ForeignKey("standard_versions.id"), nullable=False)
    rule_id = Column(String(100), unique=True, nullable=False) # R76-2006-A441-WEIGHING
    clause = Column(String(50), nullable=False)
    test_id = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    formula = Column(String(255), nullable=True)
    inputs = Column(JSON, default=list)
    unit = Column(String(20), default="e")
    limits = Column(JSON, default=dict)
    conditions = Column(JSON, default=dict)
    applicability = Column(String(255), default="ALL")
    pass_fail_logic = Column(Text, nullable=False)
    source_reference = Column(String(255), default="OIML R 76-1:2006 (E)")
    verification_status = Column(String(50), default="VERIFIED_AUTOMATED") # VERIFIED_AUTOMATED, CONFIGURED, MANUAL_REVIEW
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    version_rel = relationship("StandardVersion", back_populates="rules")

class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_number = Column(String(100), unique=True, index=True, nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    session_name = Column(String(255), nullable=False)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.DRAFT)
    overall_compliance = Column(Enum(TestStatusEnum), default=TestStatusEnum.NOT_TESTED)
    
    # Ambient Conditions
    ambient_temp = Column(Float, default=22.0)
    ambient_humidity = Column(Float, default=55.0)
    ambient_pressure = Column(Float, default=1013.25)
    ambient_voltage = Column(Float, default=230.0)
    
    test_engineer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approver_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instrument = relationship("Instrument", back_populates="test_sessions")
    observations = relationship("TestObservation", back_populates="session", cascade="all, delete-orphan")
    calculations = relationship("CalculationResult", back_populates="session", cascade="all, delete-orphan")
    compliance_results = relationship("ComplianceResult", back_populates="session", cascade="all, delete-orphan")
    evidence_files = relationship("Evidence", back_populates="session", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="session", uselist=False, cascade="all, delete-orphan")

class TestObservation(Base):
    __tablename__ = "test_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=False)
    test_code = Column(String(50), nullable=False)
    point_name = Column(String(100), nullable=False) # e.g., "Min", "500e", "Max", "Corner 1", "Run 1"
    test_load = Column(Float, nullable=False)
    observed_indication = Column(Float, nullable=False)
    delta_load = Column(Float, default=0.0) # changeover weight delta L
    calculated_error = Column(Float, nullable=True)
    corrected_error = Column(Float, nullable=True)
    mpe = Column(Float, nullable=True)
    status = Column(Enum(TestStatusEnum), default=TestStatusEnum.NOT_TESTED)
    remarks = Column(String(255), nullable=True)
    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TestSession", back_populates="observations")

class CalculationResult(Base):
    __tablename__ = "calculation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=False)
    test_code = Column(String(50), nullable=False)
    rule_id = Column(String(100), nullable=True)
    clause = Column(String(50), nullable=False)
    formula = Column(String(255), nullable=False)
    input_values = Column(JSON, default=dict)
    calculated_value = Column(Float, nullable=False)
    permissible_value = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    status = Column(Enum(TestStatusEnum), default=TestStatusEnum.PASS)
    calculation_timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("TestSession", back_populates="calculations")

class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=False)
    test_code = Column(String(50), nullable=False)
    test_name = Column(String(255), nullable=False)
    clause = Column(String(50), nullable=False)
    standard_reference = Column(String(255), default="OIML R 76-1:2006 (E)")
    observed_summary = Column(String(255), nullable=False)
    permissible_summary = Column(String(255), nullable=False)
    status = Column(Enum(TestStatusEnum), nullable=False)
    basis = Column(Text, nullable=False)
    explainability_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TestSession", back_populates="compliance_results")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=True)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=True)
    test_code = Column(String(50), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False) # SHA-256
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TestSession", back_populates="evidence_files")
    instrument = relationship("Instrument", back_populates="evidence_files")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_number = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(36), ForeignKey("test_sessions.id"), nullable=False)
    instrument_id = Column(String(36), ForeignKey("instruments.id"), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.DRAFT, nullable=False)
    overall_result = Column(Enum(TestStatusEnum), default=TestStatusEnum.NOT_TESTED)
    
    reviewer_comments = Column(Text, nullable=True)
    approver_comments = Column(Text, nullable=True)
    
    pdf_path = Column(String(500), nullable=True)
    docx_path = Column(String(500), nullable=True)
    
    generated_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    finalized_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("TestSession", back_populates="report")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")

class ReportVersion(Base):
    __tablename__ = "report_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False)
    version_str = Column(String(20), nullable=False)
    status = Column(Enum(ReportStatusEnum), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    docx_path = Column(String(500), nullable=True)
    change_summary = Column(Text, nullable=True)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report", back_populates="versions")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    user_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False) # e.g. INSTRUMENT_CREATED, REPORT_FINALIZED
    entity = Column(String(100), nullable=False) # Instrument, Report, TestSession, Rule
    entity_id = Column(String(100), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

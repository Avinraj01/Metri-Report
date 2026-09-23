import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models import (
    User, RoleEnum, AuthProviderEnum, Instrument, AccuracyClassEnum,
    TestCatalogItem, Standard, StandardVersion, StandardRule,
    TestSession, TestObservation, CalculationResult, ComplianceResult,
    Evidence, Report, ReportVersion, AuditLog, ReportStatusEnum, TestStatusEnum
)
from app.calculations.engine import CalculationEngine
from app.reports.generator_pdf import generate_pdf_report
from app.reports.generator_docx import generate_docx_report
from app.config import settings

def seed_database(db: Session):
    """
    Idempotent database seeder for METRIREPORT.
    Populates demo users, standards, full OIML test catalog, instruments, test sessions,
    calculations, compliance results, evidence files, reports, and audit logs.
    """
    # 1. Seed Users
    if db.query(User).count() == 0:
        demo_users = [
            ("admin@metrireport.local", "admin123", "Admin Officer (Legal Metrology)", RoleEnum.ADMIN),
            ("manager@metrireport.local", "manager123", "Dr. Rajesh Sharma (Lab Manager)", RoleEnum.LAB_MANAGER),
            ("engineer@metrireport.local", "engineer123", "Avinash Kumar (Lead Test Engineer)", RoleEnum.TEST_ENGINEER),
            ("reviewer@metrireport.local", "reviewer123", "Sunita Verma (Senior Reviewer)", RoleEnum.REVIEWER),
            ("viewer@metrireport.local", "viewer123", "Priya Nair (Guest Metrology Auditor)", RoleEnum.VIEWER),
        ]
        for email, pwd, name, role in demo_users:
            u = User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role,
                auth_provider=AuthProviderEnum.LOCAL,
                is_active=True
            )
            db.add(u)
        db.commit()

    admin_user = db.query(User).filter(User.email == "admin@metrireport.local").first()
    engineer_user = db.query(User).filter(User.email == "engineer@metrireport.local").first()
    reviewer_user = db.query(User).filter(User.email == "reviewer@metrireport.local").first()

    # 2. Seed Standard and Standard Versions
    standard = db.query(Standard).filter(Standard.code == "OIML R 76-1").first()
    if not standard:
        standard = Standard(
            code="OIML R 76-1",
            title="Non-automatic weighing instruments - Part 1: Metrological and technical requirements - Tests",
            organization="OIML"
        )
        db.add(standard)
        db.commit()

    std_version = db.query(StandardVersion).filter(StandardVersion.edition == "2006").first()
    if not std_version:
        std_version = StandardVersion(
            standard_id=standard.id,
            edition="2006",
            status="ACTIVE",
            effective_date=datetime(2006, 1, 1)
        )
        db.add(std_version)
        db.commit()

    # 3. Seed Rules
    if db.query(StandardRule).count() == 0:
        rules_data = [
            {
                "rule_id": "R76-2006-A423-ZERO",
                "clause": "A.4.2.3",
                "test_id": "A.4.2.3",
                "description": "Accuracy of zero-setting: Error at zero E0 = I0 + 0.5e - ΔL0 - L0 shall not exceed ±0.25e.",
                "formula": "E0 = I0 + 0.5e - ΔL0 - L0",
                "unit": "e",
                "limits": {"max_error_e": 0.25},
                "applicability": "ALL",
                "pass_fail_logic": "abs(E0) <= 0.25 * e",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.2.3",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A441-WEIGHING",
                "clause": "A.4.4.1",
                "test_id": "A.4.4.1",
                "description": "Weighing Performance Test: Error at each load step corrected for zero error Ec = E - E0 shall not exceed MPE(L).",
                "formula": "E = I + 0.5e - ΔL - L;  Ec = E - E0",
                "unit": "kg",
                "limits": {"table": "Table 6"},
                "applicability": "ALL",
                "pass_fail_logic": "abs(Ec) <= MPE(L)",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.4.1 & Cl. 3.5.1",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A47-ECCENTRICITY",
                "clause": "A.4.7",
                "test_id": "A.4.7",
                "description": "Eccentricity Test: The errors at each position shall not exceed MPE for the applied test load.",
                "formula": "L_ecc = 1/3 (Max + Tare) or 1/(N-1) (Max + Tare)",
                "unit": "kg",
                "limits": {"table": "Table 6"},
                "applicability": "ALL",
                "pass_fail_logic": "abs(Ec_i) <= MPE(L_ecc)",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.7",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A410-REPEATABILITY",
                "clause": "A.4.10",
                "test_id": "A.4.10",
                "description": "Repeatability: Difference between maximum and minimum results obtained with same load shall not exceed |MPE(L)|.",
                "formula": "ΔE = E_max - E_min",
                "unit": "kg",
                "limits": {"max_spread": "MPE(L)"},
                "applicability": "ALL",
                "pass_fail_logic": "delta_E <= MPE(L)",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.10 & Cl. 3.6.1",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A48-DISCRIMINATION",
                "clause": "A.4.8",
                "test_id": "A.4.8",
                "description": "Discrimination: Additional load of 1.4d shall cause indication to change by at least 1.0d.",
                "formula": "ΔI = I_final - I_initial",
                "unit": "d",
                "limits": {"min_change_d": 1.0, "test_load_d": 1.4},
                "applicability": "ALL",
                "pass_fail_logic": "delta_I >= 1.0 * d",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.8 & Cl. 3.8",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A4111-CREEP",
                "clause": "A.4.11.1",
                "test_id": "A.4.11.1",
                "description": "Creep Test: |I(30min) - I(0)| <= MPE(Max) and |I(30min) - I(15min)| <= 0.5e.",
                "formula": "ΔI_30 = |I(30) - I(0)|;  ΔI_15_30 = |I(30) - I(15)|",
                "unit": "kg",
                "limits": {"mpe_max": True, "interval_limit_e": 0.5},
                "applicability": "ALL",
                "pass_fail_logic": "delta_30 <= MPE and delta_15_30 <= 0.5e",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.4.11.1",
                "verification_status": "VERIFIED_AUTOMATED"
            },
            {
                "rule_id": "R76-2006-A532-TEMP-EFFECT",
                "clause": "A.5.3.2",
                "test_id": "A.5.3.2",
                "description": "Temperature effect on no-load indication: Zero drift shall not exceed 1e per 5°C (Class II, III, IIII) or 1e per 1°C (Class I).",
                "formula": "Drift_rate = |E0(T2) - E0(T1)| / |T2 - T1|",
                "unit": "e/°C",
                "limits": {"rate": "1e/5°C"},
                "applicability": "ALL",
                "pass_fail_logic": "rate <= 1e/5°C",
                "source_reference": "OIML R 76-1:2006 (E) Cl. A.5.3.2",
                "verification_status": "VERIFIED_AUTOMATED"
            }
        ]
        for rd in rules_data:
            r = StandardRule(
                version_id=std_version.id,
                rule_id=rd["rule_id"],
                clause=rd["clause"],
                test_id=rd["test_id"],
                description=rd["description"],
                formula=rd["formula"],
                unit=rd["unit"],
                limits=rd["limits"],
                applicability=rd["applicability"],
                pass_fail_logic=rd["pass_fail_logic"],
                source_reference=rd["source_reference"],
                verification_status=rd["verification_status"],
                is_active=True
            )
            db.add(r)
        db.commit()

    # 4. Seed Test Catalog
    if db.query(TestCatalogItem).count() == 0:
        catalog_data = [
            {
                "test_code": "A.1", "test_name": "Administrative Examination", "annex": "Annex A", "clause": "Clause A.1",
                "category": "Visual & Administrative", "classification": "CONFIGURED", "applicability_condition": "ALL",
                "procedure_summary": "Examine descriptive markings, verification marks, inscriptions, suitability for use and securing of metrological controls.",
                "acceptance_criteria": "All markings and documentation comply with OIML R 76-1 Section 7.", "source_reference": "OIML R 76-1:2006 Cl. A.1"
            },
            {
                "test_code": "A.2", "test_name": "Compare Construction with Documentation", "annex": "Annex A", "clause": "Clause A.2",
                "category": "Visual & Administrative", "classification": "CONFIGURED", "applicability_condition": "ALL",
                "procedure_summary": "Examine instrument construction and compare against technical drawings, schematics, and component lists.",
                "acceptance_criteria": "Instrument matches submitted type evaluation documentation exactly.", "source_reference": "OIML R 76-1:2006 Cl. A.2"
            },
            {
                "test_code": "A.3", "test_name": "Initial Examination", "annex": "Annex A", "clause": "Clause A.3",
                "category": "Visual & Functional", "classification": "CONFIGURED", "applicability_condition": "ALL",
                "procedure_summary": "Check operating condition, power supply, warmup time, display illumination, and zero/tare functions.",
                "acceptance_criteria": "Normal operation without disturbance or initialization errors.", "source_reference": "OIML R 76-1:2006 Cl. A.3"
            },
            {
                "test_code": "A.4.2.1", "test_name": "Range of Zero-Setting", "annex": "Annex A", "clause": "Clause 4.5.1 / A.4.2.1",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Determine maximum positive and negative loads that can be zeroed by zero-setting device.",
                "acceptance_criteria": "Total range complies with configured limits (-1% to +3% or ±2% of Max).", "source_reference": "OIML R 76-1:2006 Cl. 4.5.1"
            },
            {
                "test_code": "A.4.2.3", "test_name": "Accuracy of Zero-Setting", "annex": "Annex A", "clause": "Clause A.4.2.3",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Determine error at zero using changeover weights (ΔL0).",
                "acceptance_criteria": "|E0| <= 0.25e.", "source_reference": "OIML R 76-1:2006 Cl. A.4.2.3"
            },
            {
                "test_code": "A.4.4.1", "test_name": "Weighing Performance Test", "annex": "Annex A", "clause": "Clause A.4.4.1 & A.4.4.3",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Apply test loads from zero up to Max and back to zero in at least 5 increasing and decreasing steps. Determine changeover points.",
                "acceptance_criteria": "Corrected error |Ec| <= MPE(L) for all steps.", "source_reference": "OIML R 76-1:2006 Cl. A.4.4.1"
            },
            {
                "test_code": "A.4.7", "test_name": "Eccentricity Test", "annex": "Annex A", "clause": "Clause A.4.7",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Apply eccentricity load (1/3 Max or 1/(N-1) Max) to center and 4 corners/supports.",
                "acceptance_criteria": "Corrected error |Ec,i| <= MPE(L_ecc) at all positions.", "source_reference": "OIML R 76-1:2006 Cl. A.4.7"
            },
            {
                "test_code": "A.4.8", "test_name": "Discrimination Test", "annex": "Annex A", "clause": "Clause A.4.8",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "At loads Min, 1/2 Max, Max, add small load equal to 1.4d smoothly to load receptor.",
                "acceptance_criteria": "Indication must increase by at least 1.0d.", "source_reference": "OIML R 76-1:2006 Cl. A.4.8 & 3.8"
            },
            {
                "test_code": "A.4.10", "test_name": "Repeatability Test", "annex": "Annex A", "clause": "Clause A.4.10",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Execute at least 3 (or 10) series of weighings with test load around 0.5 Max or Max.",
                "acceptance_criteria": "Maximum span ΔE = E_max - E_min <= |MPE(L)|.", "source_reference": "OIML R 76-1:2006 Cl. A.4.10 & 3.6.1"
            },
            {
                "test_code": "A.4.11.1", "test_name": "Creep Test", "annex": "Annex A", "clause": "Clause A.4.11.1",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Keep load at Max for 30 min. Observe indications at 0, 15 min, and 30 min.",
                "acceptance_criteria": "|I(30) - I(0)| <= MPE(Max) and |I(30) - I(15)| <= 0.5e.", "source_reference": "OIML R 76-1:2006 Cl. A.4.11.1"
            },
            {
                "test_code": "A.4.11.2", "test_name": "Zero Return Test", "annex": "Annex A", "clause": "Clause A.4.11.2",
                "category": "Performance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Unload after 30 min Creep test. Record zero reading within 15 seconds.",
                "acceptance_criteria": "|E0_return| <= 0.5e.", "source_reference": "OIML R 76-1:2006 Cl. A.4.11.2"
            },
            {
                "test_code": "A.5.1", "test_name": "Tilting Test", "annex": "Annex A", "clause": "Clause A.5.1",
                "category": "Influence Factor", "classification": "CONFIGURED", "applicability_condition": "NOT_WEIGHBRIDGE",
                "procedure_summary": "Tilt instrument longitudinally and transversely to 50/1000 or level indicator limit.",
                "acceptance_criteria": "Errors stay within MPE.", "source_reference": "OIML R 76-1:2006 Cl. A.5.1"
            },
            {
                "test_code": "A.5.3.1", "test_name": "Static Temperatures Test", "annex": "Annex A", "clause": "Clause A.5.3.1",
                "category": "Influence Factor", "classification": "CONFIGURED", "applicability_condition": "ALL",
                "procedure_summary": "Perform weighing tests at reference temp (+20°C), Max specified temp (+40°C), Min specified temp (-10°C), and return to +20°C.",
                "acceptance_criteria": "Weighing errors conform to MPE throughout temperature span.", "source_reference": "OIML R 76-1:2006 Cl. A.5.3.1"
            },
            {
                "test_code": "A.5.3.2", "test_name": "Temperature Effect on No-Load Indication", "annex": "Annex A", "clause": "Clause A.5.3.2",
                "category": "Influence Factor", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Record zero drift across temperature transitions.",
                "acceptance_criteria": "Zero drift <= 1e per 5°C (Class II, III, IIII) or 1e per 1°C (Class I).", "source_reference": "OIML R 76-1:2006 Cl. A.5.3.2"
            },
            {
                "test_code": "A.5.4", "test_name": "Voltage Variations Test", "annex": "Annex A", "clause": "Clause A.5.4",
                "category": "Influence Factor", "classification": "AUTOMATED", "applicability_condition": "ELECTRONIC",
                "procedure_summary": "Vary mains power supply voltage between Unom - 15% and Unom + 10%.",
                "acceptance_criteria": "Weighing errors within MPE; zero shift <= 0.25e.", "source_reference": "OIML R 76-1:2006 Cl. A.5.4"
            },
            {
                "test_code": "A.6", "test_name": "Endurance Test", "annex": "Annex A", "clause": "Clause A.6",
                "category": "Endurance", "classification": "AUTOMATED", "applicability_condition": "ALL",
                "procedure_summary": "Subject load receptor to repetitive loading/unloading cycles (at least 100,000 cycles). Compare span before and after.",
                "acceptance_criteria": "Span error drift <= MPE.", "source_reference": "OIML R 76-1:2006 Cl. A.6"
            },
            {
                "test_code": "B.2", "test_name": "Damp Heat, Steady State", "annex": "Annex B", "clause": "Clause B.2",
                "category": "Electronic & Disturbance", "classification": "CONFIGURED", "applicability_condition": "ELECTRONIC",
                "procedure_summary": "Expose electronic instrument to +40°C at 85% RH for 48 hours or 4 days.",
                "acceptance_criteria": "Insulation resistance, span, and weighing errors remain within MPE.", "source_reference": "OIML R 76-1:2006 Cl. B.2"
            },
            {
                "test_code": "B.3", "test_name": "Performance Tests for Disturbances (EMC / ESD / Dips)", "annex": "Annex B", "clause": "Clause B.3",
                "category": "Electronic & Disturbance", "classification": "CONFIGURED", "applicability_condition": "ELECTRONIC",
                "procedure_summary": "Apply electrostatic discharge (ESD), electrical fast transients (bursts), and voltage dips/interruptions.",
                "acceptance_criteria": "No significant fault occurs (ΔI <= 1e or fault detected and indicated).", "source_reference": "OIML R 76-1:2006 Cl. B.3"
            },
            {
                "test_code": "B.4", "test_name": "Span Stability Test", "annex": "Annex B", "clause": "Clause B.4",
                "category": "Electronic & Disturbance", "classification": "AUTOMATED", "applicability_condition": "ELECTRONIC",
                "procedure_summary": "Measure span repeatedly over 8 measurement cycles (28 days).",
                "acceptance_criteria": "Span drift <= 0.5e across all measurement intervals.", "source_reference": "OIML R 76-1:2006 Cl. B.4"
            },
            {
                "test_code": "Annex G", "test_name": "Software-Controlled Instrument Examination", "annex": "Annex G", "clause": "Annex G (Cl. G.1 - G.4)",
                "category": "Software Requirements", "classification": "MANUAL_REVIEW", "applicability_condition": "ELECTRONIC",
                "procedure_summary": "Inspect software identification version, cryptographic checksum / SHA-256 hash, legally relevant parameter audit log counter, and data storage protections.",
                "acceptance_criteria": "Software version and checksum verified; audit event counter increments on parameter change; documentation matches binary.", "source_reference": "OIML R 76-1:2006 Annex G"
            }
        ]
        for item in catalog_data:
            c = TestCatalogItem(
                test_code=item["test_code"],
                test_name=item["test_name"],
                annex=item["annex"],
                clause=item["clause"],
                category=item["category"],
                classification=item["classification"],
                applicability_condition=item["applicability_condition"],
                procedure_summary=item["procedure_summary"],
                acceptance_criteria=item["acceptance_criteria"],
                source_reference=item["source_reference"],
                is_active=True
            )
            db.add(c)
        db.commit()

    # 5. Seed Realistic Instruments
    if db.query(Instrument).count() == 0:
        instruments_data = [
            {
                "instrument_name": "Demo Electronic Platform Scale (MW-3000)",
                "model": "MW-3000",
                "instrument_type": "Electronic Platform Scale",
                "serial_number": "MW3000-2026-IND-001",
                "manufacturer": "Demo WeighTech Pvt. Ltd.",
                "manufacturer_address": "Plot 45, Okhla Industrial Area Phase III, New Delhi 110020, India",
                "applicant_name": "Demo WeighTech Pvt. Ltd.",
                "applicant_address": "Plot 45, Okhla Industrial Area Phase III, New Delhi 110020, India",
                "accuracy_class": AccuracyClassEnum.CLASS_III,
                "max_capacity": 3000.0,
                "min_capacity": 20.0,
                "e_value": 1.0,
                "d_value": 1.0,
                "n_intervals": 3000,
                "unit": "kg",
                "num_ranges": 1,
                "is_multi_range": False,
                "is_multi_interval": False,
                "is_electronic": True,
                "is_self_indicating": True,
                "is_mobile": False,
                "is_portable": False,
                "is_weighbridge": False,
                "load_receptor_type": "Platform",
                "num_support_points": 4,
                "load_cell_details": "4x Zemic H8C Shear Beam Load Cells (OIML R60 C3)",
                "indicator_details": "WeighTech WT-IND-800 LED Digital Indicator",
                "software_version": "v2.4.1",
                "firmware_id": "FW-MW3000-REV4",
                "power_supply": "230 V AC, 50 Hz",
                "temp_min": -10.0,
                "temp_max": 40.0,
                "humidity_min": 20.0,
                "humidity_max": 85.0,
                "voltage_nominal": 230.0,
                "voltage_min": 195.5,
                "voltage_max": 253.0,
                "country_of_manufacture": "India",
                "application_use": "Industrial Warehouse and Logistics Weight Verification",
                "status": "EVALUATED"
            },
            {
                "instrument_name": "Precision Laboratory Balance (PB-600)",
                "model": "PB-600",
                "instrument_type": "Precision Electronic Balance",
                "serial_number": "PB600-2026-IND-082",
                "manufacturer": "Precision Balances India Ltd.",
                "manufacturer_address": "Peenya Industrial Area, Bengaluru 560058, Karnataka",
                "applicant_name": "Precision Balances India Ltd.",
                "applicant_address": "Peenya Industrial Area, Bengaluru 560058, Karnataka",
                "accuracy_class": AccuracyClassEnum.CLASS_II,
                "max_capacity": 600.0,
                "min_capacity": 0.5,
                "e_value": 0.01,
                "d_value": 0.001,
                "n_intervals": 60000,
                "unit": "g",
                "is_electronic": True,
                "load_receptor_type": "Stainless Pan",
                "num_support_points": 1,
                "load_cell_details": "Electromagnetic Force Compensation Cell",
                "software_version": "v1.1.0",
                "status": "REGISTERED"
            },
            {
                "instrument_name": "Analytical Micro-Balance (AB-220)",
                "model": "AB-220",
                "instrument_type": "Analytical Balance",
                "serial_number": "AB220-2026-IND-019",
                "manufacturer": "Apex Analytical Instruments",
                "manufacturer_address": "MIDC Industrial Area, Pune 411019, Maharashtra",
                "applicant_name": "Apex Analytical Instruments",
                "applicant_address": "MIDC Industrial Area, Pune 411019, Maharashtra",
                "accuracy_class": AccuracyClassEnum.CLASS_I,
                "max_capacity": 220.0,
                "min_capacity": 0.01,
                "e_value": 0.001,
                "d_value": 0.0001,
                "n_intervals": 220000,
                "unit": "g",
                "is_electronic": True,
                "load_receptor_type": "Draft-Shielded Pan",
                "num_support_points": 1,
                "software_version": "v3.0.4",
                "status": "REGISTERED"
            },
            {
                "instrument_name": "Heavy Road Weighbridge (WB-50K)",
                "model": "WB-50K",
                "instrument_type": "Pitless Road Weighbridge",
                "serial_number": "WB50K-2026-IND-004",
                "manufacturer": "Bharat Weighbridge Systems Ltd.",
                "manufacturer_address": "Sanand Industrial Estate, Ahmedabad 382110, Gujarat",
                "applicant_name": "National Highways Logistics Authority",
                "applicant_address": "Transport Bhawan, New Delhi 110001",
                "accuracy_class": AccuracyClassEnum.CLASS_III,
                "max_capacity": 50000.0,
                "min_capacity": 400.0,
                "e_value": 10.0,
                "d_value": 10.0,
                "n_intervals": 5000,
                "unit": "kg",
                "is_weighbridge": True,
                "load_receptor_type": "Steel Deck",
                "num_support_points": 6,
                "load_cell_details": "6x 20t Compression Column Load Cells",
                "status": "EVALUATED"
            },
            {
                "instrument_name": "Retail Price-Computing Scale (RL-30)",
                "model": "RL-30",
                "instrument_type": "Price-Computing Scale",
                "serial_number": "RL30-2026-IND-551",
                "manufacturer": "Retail Scales Co.",
                "manufacturer_address": "Guindy Industrial Estate, Chennai 600032, Tamil Nadu",
                "applicant_name": "Retail Scales Co.",
                "applicant_address": "Guindy Industrial Estate, Chennai 600032, Tamil Nadu",
                "accuracy_class": AccuracyClassEnum.CLASS_III,
                "max_capacity": 30.0,
                "min_capacity": 0.1,
                "e_value": 0.005,
                "d_value": 0.005,
                "n_intervals": 6000,
                "unit": "kg",
                "is_electronic": True,
                "status": "REGISTERED"
            }
        ]
        for idata in instruments_data:
            inst = Instrument(**idata)
            db.add(inst)
        db.commit()

    # 6. Seed Complete Test Sessions & Completed Evaluations
    mw3000 = db.query(Instrument).filter(Instrument.model == "MW-3000").first()
    if mw3000 and db.query(TestSession).filter(TestSession.instrument_id == mw3000.id).count() == 0:
        # Session 1: SUCCESSFUL PASS EVALUATION
        session_pass = TestSession(
            session_number="TS-2026-001-MW3000",
            instrument_id=mw3000.id,
            session_name="Full Type-Evaluation Testing (Pass Baseline)",
            status=ReportStatusEnum.FINALIZED,
            overall_compliance=TestStatusEnum.PASS,
            ambient_temp=22.4,
            ambient_humidity=52.0,
            ambient_pressure=1012.8,
            ambient_voltage=230.2,
            test_engineer_id=engineer_user.id if engineer_user else None,
            reviewer_id=reviewer_user.id if reviewer_user else None,
            approver_id=admin_user.id if admin_user else None,
            notes="Comprehensive OIML R-76 type-evaluation completed. Full compliance with Table 6 MPE limits verified."
        )
        db.add(session_pass)
        db.commit()

        # Add Observations for Session 1
        # A.4.2.3 Zero
        obs_zero = TestObservation(
            session_id=session_pass.id,
            test_code="A.4.2.3",
            point_name="Zero Setting",
            test_load=0.0,
            observed_indication=0.0,
            delta_load=0.45, # delta L = 0.45 kg -> E0 = 0 + 0.5 - 0.45 - 0 = +0.05 kg (within 0.25e = 0.25 kg)
            remarks="Zero-setting error within ±0.25e"
        )
        db.add(obs_zero)

        # A.4.4.1 Weighing points
        weigh_loads = [
            ("Min (20 kg)", 20.0, 20.0, 0.48),        # Ec = +0.02 - 0.05 = -0.03 kg (MPE = 0.5 kg)
            ("500e (500 kg)", 500.0, 500.0, 0.42),     # Ec = +0.08 - 0.05 = +0.03 kg (MPE = 0.5 kg)
            ("1000 kg", 1000.0, 1000.0, 0.35),        # Ec = +0.15 - 0.05 = +0.10 kg (MPE = 1.0 kg)
            ("2000e (2000 kg)", 2000.0, 2000.0, 0.30),# Ec = +0.20 - 0.05 = +0.15 kg (MPE = 1.0 kg)
            ("Max (3000 kg)", 3000.0, 3000.0, 0.25),  # Ec = +0.25 - 0.05 = +0.20 kg (MPE = 1.5 kg)
        ]
        for pt_name, load, ind, dl in weigh_loads:
            o = TestObservation(
                session_id=session_pass.id,
                test_code="A.4.4.1",
                point_name=pt_name,
                test_load=load,
                observed_indication=ind,
                delta_load=dl,
                remarks="Ascending step verification"
            )
            db.add(o)

        # A.4.7 Eccentricity (1/3 Max = 1000 kg)
        ecc_positions = [
            ("Center", 1000.0, 1000.0, 0.45),
            ("Front-Left", 1000.0, 1000.0, 0.40),
            ("Front-Right", 1000.0, 1000.0, 0.38),
            ("Rear-Left", 1000.0, 1000.0, 0.42),
            ("Rear-Right", 1000.0, 1000.0, 0.36),
        ]
        for pos_name, load, ind, dl in ecc_positions:
            o = TestObservation(
                session_id=session_pass.id,
                test_code="A.4.7",
                point_name=pos_name,
                test_load=load,
                observed_indication=ind,
                delta_load=dl,
                remarks="Corner eccentricity test"
            )
            db.add(o)

        # A.4.10 Repeatability (1500 kg, 3 runs)
        rep_runs = [
            ("Run 1", 1500.0, 1500.0, 0.40),
            ("Run 2", 1500.0, 1500.0, 0.42),
            ("Run 3", 1500.0, 1500.0, 0.39),
        ]
        for run_name, load, ind, dl in rep_runs:
            o = TestObservation(
                session_id=session_pass.id,
                test_code="A.4.10",
                point_name=run_name,
                test_load=load,
                observed_indication=ind,
                delta_load=dl,
                remarks="Repeatability cycle"
            )
            db.add(o)

        db.commit()

        # Run calculations for Session 1
        CalculationEngine.run_session_calculations(db, session_pass.id)

        # Create Report for Session 1
        rep_pass = Report(
            report_number="REP-2026-OIML-001",
            session_id=session_pass.id,
            instrument_id=mw3000.id,
            version="1.0",
            status=ReportStatusEnum.FINALIZED,
            overall_result=TestStatusEnum.PASS,
            reviewer_comments="All metrological parameters comply with OIML R 76-1:2006 Class III requirements. Ready for final prototype signoff.",
            approver_comments="Approved for SIH 2026 Legal Metrology Evaluation Demonstration.",
            generated_by_id=engineer_user.id if engineer_user else None,
            reviewed_by_id=reviewer_user.id if reviewer_user else None,
            approved_by_id=admin_user.id if admin_user else None,
            finalized_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(rep_pass)
        db.commit()

        # Generate sample PDF and DOCX files for this report
        pdf_file = os.path.join(settings.UPLOAD_DIR, f"report_{rep_pass.id}.pdf")
        docx_file = os.path.join(settings.UPLOAD_DIR, f"report_{rep_pass.id}.docx")
        generate_pdf_report(rep_pass, pdf_file)
        generate_docx_report(rep_pass, docx_file)
        rep_pass.pdf_path = f"/api/reports/{rep_pass.id}/pdf"
        rep_pass.docx_path = f"/api/reports/{rep_pass.id}/docx"
        db.commit()

        # Session 2: EVALUATION WITH A FAILURE (Corner Error exceeds MPE)
        session_fail = TestSession(
            session_number="TS-2026-002-FAIL-DEMO",
            instrument_id=mw3000.id,
            session_name="Quality Defect Simulation (Corner Eccentricity Failure)",
            status=ReportStatusEnum.UNDER_REVIEW,
            overall_compliance=TestStatusEnum.FAIL,
            ambient_temp=23.0,
            ambient_humidity=50.0,
            ambient_pressure=1013.0,
            ambient_voltage=230.0,
            test_engineer_id=engineer_user.id if engineer_user else None,
            reviewer_id=reviewer_user.id if reviewer_user else None,
            notes="Simulated load cell mechanical misalignment causing excessive error on Rear-Right corner."
        )
        db.add(session_fail)
        db.commit()

        # Add observations with deliberate failure in eccentricity
        db.add(TestObservation(session_id=session_fail.id, test_code="A.4.2.3", point_name="Zero", test_load=0.0, observed_indication=0.0, delta_load=0.5))
        db.add(TestObservation(session_id=session_fail.id, test_code="A.4.4.1", point_name="500 kg", test_load=500.0, observed_indication=500.0, delta_load=0.5))
        # Rear-Right corner has high deviation: delta_load = -1.2 -> Error = +1.7 kg > MPE (1.0 kg)
        db.add(TestObservation(session_id=session_fail.id, test_code="A.4.7", point_name="Center", test_load=1000.0, observed_indication=1000.0, delta_load=0.5))
        db.add(TestObservation(session_id=session_fail.id, test_code="A.4.7", point_name="Rear-Right (Faulty)", test_load=1000.0, observed_indication=1002.0, delta_load=0.1, remarks="Exceeds permissible corner error"))
        db.commit()

        CalculationEngine.run_session_calculations(db, session_fail.id)

        rep_fail = Report(
            report_number="REP-2026-OIML-002-FAIL",
            session_id=session_fail.id,
            instrument_id=mw3000.id,
            version="1.0",
            status=ReportStatusEnum.UNDER_REVIEW,
            overall_result=TestStatusEnum.FAIL,
            reviewer_comments="Failure detected: Rear-Right corner eccentricity exceeds MPE (1.0 kg). Non-compliant with OIML R 76-1 Cl. A.4.7.",
            generated_by_id=engineer_user.id if engineer_user else None
        )
        db.add(rep_fail)
        db.commit()

        # Session 3: MANUAL REVIEW REQUIRED (Software Annex G)
        session_manual = TestSession(
            session_number="TS-2026-003-MANUAL-REVIEW",
            instrument_id=mw3000.id,
            session_name="Software Examination & Integrity Audit",
            status=ReportStatusEnum.READY_FOR_REVIEW,
            overall_compliance=TestStatusEnum.MANUAL_REVIEW,
            test_engineer_id=engineer_user.id if engineer_user else None,
            notes="Annex G software verification: Firmware hash matches, parameter audit counter verified."
        )
        db.add(session_manual)
        db.commit()

        comp_manual = ComplianceResult(
            session_id=session_manual.id,
            test_code="Annex G",
            test_name="Software-Controlled Instrument Examination",
            clause="Annex G (Cl. G.1 - G.4)",
            standard_reference="OIML R 76-1:2006 (E)",
            observed_summary="Software ID v2.4.1 | SHA-256: 8f4a2... | Audit Counter: 0042",
            permissible_summary="Statutory Software Inspection Verification",
            status=TestStatusEnum.MANUAL_REVIEW,
            basis="Cryptographic checksum and legally relevant parameter protection require manual expert certification inspection.",
            explainability_json={"software_version": "v2.4.1", "firmware_hash": "8f4a2b1c9e78553f"}
        )
        db.add(comp_manual)
        db.commit()

        # 7. Seed Initial Audit Logs
        audit_entries = [
            ("INSTRUMENT_REGISTERED", "Instrument", mw3000.id, "admin@metrireport.local", {"model": "MW-3000", "class": "III"}),
            ("TEST_SESSION_STARTED", "TestSession", session_pass.id, "engineer@metrireport.local", {"session": "TS-2026-001-MW3000"}),
            ("CALCULATIONS_EXECUTED", "CalculationEngine", session_pass.id, "engineer@metrireport.local", {"status": "PASS", "points": 14}),
            ("REPORT_FINALIZED", "Report", rep_pass.id, "admin@metrireport.local", {"report_number": "REP-2026-OIML-001", "status": "FINALIZED"}),
        ]
        for action, entity, eid, email, payload in audit_entries:
            db.add(AuditLog(
                user_email=email,
                action=action,
                entity=entity,
                entity_id=str(eid),
                new_values=payload,
                ip_address="127.0.0.1",
                timestamp=datetime.utcnow() - timedelta(days=1)
            ))
        db.commit()

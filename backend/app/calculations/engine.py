from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import (
    TestSession, Instrument, TestObservation, CalculationResult, ComplianceResult,
    TestStatusEnum, ReportStatusEnum
)
from app.calculations.mpe import calculate_mpe_for_load
from app.calculations.weighing import evaluate_weighing_point
from app.calculations.zero import evaluate_zero_setting_accuracy
from app.calculations.repeatability import evaluate_repeatability_series
from app.calculations.eccentricity import evaluate_eccentricity_test
from app.calculations.discrimination import evaluate_discrimination_test
from app.calculations.creep import evaluate_creep_test, evaluate_zero_return_test
from app.calculations.influence import evaluate_temp_effect_on_no_load, evaluate_voltage_variation
from app.calculations.electronic import evaluate_span_stability

class CalculationEngine:
    @staticmethod
    def run_session_calculations(db: Session, session_id: str) -> Dict[str, Any]:
        """
        Executes all mathematical evaluations for observations registered in a TestSession.
        Saves CalculationResult and ComplianceResult entries to the database.
        """
        test_session = db.query(TestSession).filter(TestSession.id == session_id).first()
        if not test_session:
            raise ValueError(f"TestSession {session_id} not found")

        instrument = test_session.instrument
        if not instrument:
            raise ValueError(f"Instrument not associated with session {session_id}")

        # Clear existing calculations and compliance results for fresh run
        db.query(CalculationResult).filter(CalculationResult.session_id == session_id).delete()
        db.query(ComplianceResult).filter(ComplianceResult.session_id == session_id).delete()

        observations: List[TestObservation] = db.query(TestObservation).filter(
            TestObservation.session_id == session_id
        ).all()

        # Group observations by test_code
        obs_by_test: Dict[str, List[TestObservation]] = {}
        for obs in observations:
            obs_by_test.setdefault(obs.test_code, []).append(obs)

        # First, find zero error E0 from A.4.2.3 or zero point observation
        zero_error = 0.0
        zero_obs = [o for o in observations if o.test_code == "A.4.2.3" or o.point_name.lower() in ["zero", "0", "0e"]]
        if zero_obs:
            first_z = zero_obs[0]
            z_eval = evaluate_zero_setting_accuracy(first_z.observed_indication, instrument.e_value, first_z.delta_load, first_z.test_load)
            zero_error = z_eval["zero_error"]

        overall_status_list = []

        # 1. Evaluate A.4.2.3 Zero-setting accuracy
        if "A.4.2.3" in obs_by_test:
            for obs in obs_by_test["A.4.2.3"]:
                res = evaluate_zero_setting_accuracy(obs.observed_indication, instrument.e_value, obs.delta_load, obs.test_load)
                obs.calculated_error = res["zero_error"]
                obs.corrected_error = res["zero_error"]
                obs.mpe = res["limit"]
                obs.status = res["status"]

                calc = CalculationResult(
                    session_id=session_id,
                    test_code="A.4.2.3",
                    rule_id="R76-2006-A423-ZERO",
                    clause="OIML R 76-1:2006 Cl. A.4.2.3",
                    formula=res["formula"],
                    input_values={"indicated": obs.observed_indication, "delta_load": obs.delta_load, "load": obs.test_load},
                    calculated_value=res["zero_error"],
                    permissible_value=res["limit"],
                    margin=res["margin"],
                    unit=instrument.unit,
                    status=res["status"]
                )
                db.add(calc)

                comp = ComplianceResult(
                    session_id=session_id,
                    test_code="A.4.2.3",
                    test_name="Accuracy of Zero-Setting",
                    clause="Clause A.4.2.3",
                    standard_reference="OIML R 76-1:2006 (E)",
                    observed_summary=f"E0 = {res['zero_error']:+.3f} {instrument.unit}",
                    permissible_summary=f"Limit = ±{res['limit']:.3f} {instrument.unit} (0.25e)",
                    status=res["status"],
                    basis=f"Calculated zero error {res['zero_error']:+.3f} {instrument.unit} against permissible limit ±{res['limit']:.3f} {instrument.unit}.",
                    explainability_json=res
                )
                db.add(comp)
                overall_status_list.append(res["status"])

        # 2. Evaluate A.4.4.1 Weighing Performance Test
        if "A.4.4.1" in obs_by_test:
            weighing_points = obs_by_test["A.4.4.1"]
            weigh_pass = True
            for obs in weighing_points:
                res = evaluate_weighing_point(
                    accuracy_class=instrument.accuracy_class,
                    load=obs.test_load,
                    indicated=obs.observed_indication,
                    e_val=instrument.e_value,
                    delta_load=obs.delta_load,
                    zero_error=zero_error
                )
                obs.calculated_error = res["error"]
                obs.corrected_error = res["corrected_error"]
                obs.mpe = res["mpe"]
                obs.status = res["status"]
                if res["status"] != TestStatusEnum.PASS:
                    weigh_pass = False

                calc = CalculationResult(
                    session_id=session_id,
                    test_code="A.4.4.1",
                    rule_id=f"R76-2006-A441-{obs.point_name}",
                    clause="OIML R 76-1:2006 Cl. A.4.4.1 & A.4.4.3",
                    formula=res["formula"],
                    input_values={"load": obs.test_load, "indicated": obs.observed_indication, "delta_load": obs.delta_load, "zero_error": zero_error},
                    calculated_value=res["corrected_error"],
                    permissible_value=res["mpe"],
                    margin=res["margin"],
                    unit=instrument.unit,
                    status=res["status"]
                )
                db.add(calc)

            max_err = max([abs(o.corrected_error or 0.0) for o in weighing_points]) if weighing_points else 0.0
            comp = ComplianceResult(
                session_id=session_id,
                test_code="A.4.4.1",
                test_name="Weighing Performance Test",
                clause="Clause A.4.4.1 & A.4.4.3",
                standard_reference="OIML R 76-1:2006 (E)",
                observed_summary=f"{len(weighing_points)} points evaluated (Max |Ec| = {max_err:.3f} {instrument.unit})",
                permissible_summary=f"Tiered MPE as per Table 6 for Class {instrument.accuracy_class.value}",
                status=TestStatusEnum.PASS if weigh_pass else TestStatusEnum.FAIL,
                basis=f"All {len(weighing_points)} load changeover error steps conform to Table 6 MPE." if weigh_pass else "One or more points exceeded permissible MPE limits.",
                explainability_json={"total_points": len(weighing_points), "max_abs_error": max_err}
            )
            db.add(comp)
            overall_status_list.append(TestStatusEnum.PASS if weigh_pass else TestStatusEnum.FAIL)

        # 3. Evaluate A.4.7 Eccentricity Test
        if "A.4.7" in obs_by_test:
            ecc_points = obs_by_test["A.4.7"]
            positions_data = []
            for obs in ecc_points:
                positions_data.append({
                    "position": obs.point_name,
                    "test_load": obs.test_load,
                    "indicated": obs.observed_indication,
                    "delta_load": obs.delta_load
                })
            res_ecc = evaluate_eccentricity_test(
                accuracy_class=instrument.accuracy_class,
                max_capacity=instrument.max_capacity,
                e_val=instrument.e_value,
                num_support_points=instrument.num_support_points,
                positions=positions_data,
                zero_error=zero_error
            )
            for idx, p in enumerate(res_ecc["positions"]):
                if idx < len(ecc_points):
                    ecc_points[idx].calculated_error = p["error"]
                    ecc_points[idx].corrected_error = p["corrected_error"]
                    ecc_points[idx].mpe = p["mpe"]
                    ecc_points[idx].status = p["status"]

            calc = CalculationResult(
                session_id=session_id,
                test_code="A.4.7",
                rule_id="R76-2006-A47-ECCENTRICITY",
                clause="OIML R 76-1:2006 Cl. A.4.7",
                formula=res_ecc["formula"],
                input_values={"nominal_load": res_ecc["nominal_load"], "support_points": instrument.num_support_points},
                calculated_value=max([abs(p["corrected_error"]) for p in res_ecc["positions"]]) if res_ecc["positions"] else 0.0,
                permissible_value=res_ecc["mpe"],
                margin=min([p["margin"] for p in res_ecc["positions"]]) if res_ecc["positions"] else 0.0,
                unit=instrument.unit,
                status=res_ecc["overall_status"]
            )
            db.add(calc)

            comp = ComplianceResult(
                session_id=session_id,
                test_code="A.4.7",
                test_name="Eccentricity Test",
                clause="Clause A.4.7",
                standard_reference="OIML R 76-1:2006 (E)",
                observed_summary=f"Max eccentricity error = {calc.calculated_value:.3f} {instrument.unit}",
                permissible_summary=f"Limit = ±{res_ecc['mpe']:.3f} {instrument.unit}",
                status=res_ecc["overall_status"],
                basis=f"Load of {res_ecc['nominal_load']} {instrument.unit} evaluated across {len(positions_data)} positions.",
                explainability_json=res_ecc
            )
            db.add(comp)
            overall_status_list.append(res_ecc["overall_status"])

        # 4. Evaluate A.4.10 Repeatability Test
        if "A.4.10" in obs_by_test:
            rep_points = obs_by_test["A.4.10"]
            readings = [{"indicated": o.observed_indication, "delta_load": o.delta_load} for o in rep_points]
            test_load = rep_points[0].test_load if rep_points else instrument.max_capacity * 0.5
            res_rep = evaluate_repeatability_series(
                accuracy_class=instrument.accuracy_class,
                load=test_load,
                e_val=instrument.e_value,
                readings=readings
            )
            if res_rep.get("status") in [TestStatusEnum.PASS, TestStatusEnum.FAIL]:
                for o in rep_points:
                    o.status = res_rep["status"]
                    o.mpe = res_rep["mpe"]

                calc = CalculationResult(
                    session_id=session_id,
                    test_code="A.4.10",
                    rule_id="R76-2006-A410-REPEATABILITY",
                    clause="OIML R 76-1:2006 Cl. A.4.10",
                    formula=res_rep["formula"],
                    input_values={"load": test_load, "runs": res_rep["runs_count"]},
                    calculated_value=res_rep["repeatability_range"],
                    permissible_value=res_rep["mpe"],
                    margin=res_rep["margin"],
                    unit=instrument.unit,
                    status=res_rep["status"]
                )
                db.add(calc)

                comp = ComplianceResult(
                    session_id=session_id,
                    test_code="A.4.10",
                    test_name="Repeatability Test",
                    clause="Clause A.4.10 & 3.6.1",
                    standard_reference="OIML R 76-1:2006 (E)",
                    observed_summary=f"ΔE (Max-Min) = {res_rep['repeatability_range']:.3f} {instrument.unit}",
                    permissible_summary=f"Limit = {res_rep['mpe']:.3f} {instrument.unit}",
                    status=res_rep["status"],
                    basis=f"Repeatability difference ΔE across {res_rep['runs_count']} series evaluated against |MPE|.",
                    explainability_json=res_rep
                )
                db.add(comp)
                overall_status_list.append(res_rep["status"])

        # Determine overall session compliance status
        from app.models import TestCatalogItem
        from app.rules.applicability import ApplicabilityEngine

        catalog_items = db.query(TestCatalogItem).filter(TestCatalogItem.is_active == True).all()
        applicable_tests = ApplicabilityEngine.get_applicable_tests(instrument, catalog_items) if catalog_items else []
        applicable_codes = {item["test_code"] for item in applicable_tests if item.get("is_applicable")}
        executed_codes = set(obs_by_test.keys())

        if not overall_status_list:
            session_compliance = TestStatusEnum.NOT_TESTED
        elif any(s == TestStatusEnum.FAIL for s in overall_status_list):
            session_compliance = TestStatusEnum.FAIL
        else:
            unexecuted_applicable = applicable_codes - executed_codes
            has_manual_or_blocked = any(s in [TestStatusEnum.MANUAL_REVIEW, TestStatusEnum.BLOCKED, TestStatusEnum.NOT_TESTED] for s in overall_status_list)
            if unexecuted_applicable or has_manual_or_blocked:
                # Incomplete evaluation: some applicable tests are not tested or pending
                session_compliance = TestStatusEnum.MANUAL_REVIEW
            elif all(s == TestStatusEnum.PASS for s in overall_status_list):
                session_compliance = TestStatusEnum.PASS
            else:
                session_compliance = TestStatusEnum.MANUAL_REVIEW

        test_session.overall_compliance = session_compliance
        test_session.status = ReportStatusEnum.IN_PROGRESS
        db.commit()

        return {
            "session_id": session_id,
            "overall_compliance": session_compliance,
            "calculations_count": len(overall_status_list),
            "applicable_tests_count": len(applicable_codes),
            "executed_tests_count": len(executed_codes)
        }

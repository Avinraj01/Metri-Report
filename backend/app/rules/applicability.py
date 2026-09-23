from typing import List, Dict, Any
from app.models import Instrument, TestCatalogItem, AccuracyClassEnum

class ApplicabilityEngine:
    @staticmethod
    def get_applicable_tests(instrument: Instrument, catalog_items: List[TestCatalogItem]) -> List[Dict[str, Any]]:
        """
        Determines applicability of OIML R-76 test procedures for a specific instrument
        based on metrological characteristics (Class, Electronic, Mobile, Multi-interval, etc.).
        """
        results = []
        for item in catalog_items:
            is_applicable = True
            reason = "Applicable to all NAWI instruments."

            # Check Electronic requirements
            if item.annex == "Annex B" and not instrument.is_electronic:
                is_applicable = False
                reason = "Applies only to electronic weighing instruments (OIML R 76-1 Cl. B.1)."

            # Check Tilting test (A.5.1)
            if item.test_code == "A.5.1":
                if instrument.is_weighbridge:
                    is_applicable = False
                    reason = "Not applicable to permanently installed weighbridges."
                elif not instrument.is_mobile and not instrument.is_portable and instrument.accuracy_class == AccuracyClassEnum.CLASS_I:
                    is_applicable = False
                    reason = "Class I non-portable instruments exempt from standard tilting test if fitted with level indicator."

            # Check Annex G Software requirements
            if item.annex == "Annex G":
                if not instrument.is_electronic or not instrument.software_version:
                    is_applicable = False
                    reason = "Applicable only to software-controlled electronic instruments."

            # Check Module testing (Annex C-F)
            if item.annex in ["Annex C", "Annex D", "Annex E", "Annex F"]:
                if instrument.load_receptor_type != "Module Only":
                    is_applicable = False
                    reason = "Applicable when evaluating standalone weighing modules or indicators separately."

            results.append({
                "test_code": item.test_code,
                "test_name": item.test_name,
                "annex": item.annex,
                "clause": item.clause,
                "category": item.category,
                "classification": item.classification,
                "is_applicable": is_applicable,
                "applicability_reason": reason,
                "procedure_summary": item.procedure_summary,
                "acceptance_criteria": item.acceptance_criteria,
                "source_reference": item.source_reference
            })

        return results

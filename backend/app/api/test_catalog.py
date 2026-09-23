from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import TestCatalogItem, Instrument, User
from app.rules.applicability import ApplicabilityEngine
from app.api.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/tests", tags=["Test Catalog & Applicability"])

@router.get("/catalog")
def get_full_test_catalog(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    """
    Returns the complete catalog of configured OIML R 76-1:2006 test procedures.
    """
    return db.query(TestCatalogItem).filter(TestCatalogItem.is_active == True).all()

@router.get("/applicable/{instrument_id}")
def get_applicable_tests_for_instrument(
    instrument_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Evaluates dynamic applicability of all OIML R 76 tests for a specific instrument
    based on its Accuracy Class, load cell count, electronic flags, and usage type.
    """
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instrument not found")

    catalog = db.query(TestCatalogItem).filter(TestCatalogItem.is_active == True).all()
    applicable_results = ApplicabilityEngine.get_applicable_tests(instrument, catalog)
    return applicable_results

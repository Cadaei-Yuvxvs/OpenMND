from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ml_service import MLService

router = APIRouter()
ml_service = MLService()

@router.get("/themes")
async def get_research_themes(db: Session = Depends(get_db)):
    """Get current research themes"""
    # This will be expanded in later phases
    return {"message": "Research themes endpoint - coming soon"}

@router.get("/gaps")
async def identify_research_gaps(db: Session = Depends(get_db)):
    """Identify potential research gaps"""
    # This will be expanded in later phases
    return {"message": "Research gaps analysis - coming soon"}

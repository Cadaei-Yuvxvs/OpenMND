from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

@router.get("/trends")
async def get_research_trends(db: Session = Depends(get_db)):
    """Get research trends over time"""
    # This will be expanded in later phases
    return {"message": "Research trends analytics - coming soon"}

@router.get("/metrics")
async def get_platform_metrics(db: Session = Depends(get_db)):
    """Get platform usage metrics"""
    # This will be expanded in later phases  
    return {"message": "Platform metrics - coming soon"}

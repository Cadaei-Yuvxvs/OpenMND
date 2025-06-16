from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.research_paper import ResearchPaper
from app.services.pubmed_service import PubMedService
from app.services.ml_service import MLService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for API
class PaperResponse(BaseModel):
    id: int
    pubmed_id: str
    title: str
    abstract: Optional[str]
    authors: List[str]
    journal: str
    publication_date: Optional[datetime]
    summary: Optional[str]
    themes: Optional[List[str]]
    sentiment_score: Optional[int]
    complexity_score: Optional[int]

class SearchRequest(BaseModel):
    query: str
    max_results: int = 100

# Initialize services
pubmed_service = PubMedService()
ml_service = MLService()

@router.get("/", response_model=List[PaperResponse])
async def get_papers(
    skip: int = 0,
    limit: int = 20,
    theme: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get papers with optional filtering"""
    query = db.query(ResearchPaper)
    
    if theme:
        # Filter by theme (simplified - in production, use proper JSONB queries)
        query = query.filter(ResearchPaper.themes.contains([theme]))
    
    papers = query.offset(skip).limit(limit).all()
    
    return [
        PaperResponse(
            id=paper.id,
            pubmed_id=paper.pubmed_id,
            title=paper.title,
            abstract=paper.abstract,
            authors=paper.authors or [],
            journal=paper.journal or "",
            publication_date=paper.publication_date,
            summary=paper.summary,
            themes=paper.themes or [],
            sentiment_score=paper.sentiment_score,
            complexity_score=paper.complexity_score
        )
        for paper in papers
    ]

@router.post("/search")
async def search_and_import_papers(
    search_request: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Search PubMed and import new papers"""
    
    # Add background task for processing
    background_tasks.add_task(
        process_new_papers,
        search_request.query,
        search_request.max_results,
        db
    )
    
    return {"message": "Search initiated. Papers will be processed in background."}

def process_new_papers(query: str, max_results: int, db: Session):
    """Background task to search and process papers"""
    try:
        # Search PubMed
        pmids = pubmed_service.search_papers(query, max_results)
        
        if not pmids:
            return
        
        # Fetch paper details
        papers_data = pubmed_service.fetch_paper_details(pmids)
        
        for paper_data in papers_data:
            # Check if paper already exists
            existing = db.query(ResearchPaper).filter(
                ResearchPaper.pubmed_id == paper_data["pubmed_id"]
            ).first()
            
            if existing:
                continue
            
            # Create new paper record
            paper = ResearchPaper(
                pubmed_id=paper_data["pubmed_id"],
                title=paper_data["title"],
                abstract=paper_data["abstract"],
                authors=paper_data["authors"],
                journal=paper_data["journal"],
                publication_date=paper_data["publication_date"],
                doi=paper_data["doi"],
                mesh_terms=paper_data["mesh_terms"]
            )
            
            # Process with ML if abstract exists
            if paper_data["abstract"]:
                paper.summary = ml_service.generate_summary(paper_data["abstract"])
                sentiment = ml_service.analyze_sentiment(paper_data["abstract"])
                paper.sentiment_score = sentiment["score"]
                paper.complexity_score = ml_service.calculate_complexity_score(
                    paper_data["abstract"]
                )
                paper.is_processed = True
            
            db.add(paper)
        
        db.commit()
        
        # Extract themes from all papers
        update_global_themes(db)
        
    except Exception as e:
        print(f"Error processing papers: {e}")
        db.rollback()

def update_global_themes(db: Session):
    """Update global themes based on all papers"""
    try:
        # Get all processed papers
        papers = db.query(ResearchPaper).filter(
            ResearchPaper.is_processed == True,
            ResearchPaper.abstract.isnot(None)
        ).all()
        
        if len(papers) < 5:
            return
        
        abstracts = [paper.abstract for paper in papers]
        themes = ml_service.extract_themes(abstracts, n_themes=20)
        
        # Update papers with theme information
        for paper in papers:
            if paper.abstract:
                # Simple theme assignment (in production, use more sophisticated matching)
                paper_themes = []
                for theme in themes[:5]:  # Assign top 5 themes to each paper
                    theme_keywords = theme.get("keywords", [])
                    if any(keyword.lower() in paper.abstract.lower() for keyword in theme_keywords):
                        paper_themes.append(theme["name"])
                
                paper.themes = paper_themes
        
        db.commit()
        
    except Exception as e:
        print(f"Error updating themes: {e}")
        db.rollback()

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Get a specific paper by ID"""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return PaperResponse(
        id=paper.id,
        pubmed_id=paper.pubmed_id,
        title=paper.title,
        abstract=paper.abstract,
        authors=paper.authors or [],
        journal=paper.journal or "",
        publication_date=paper.publication_date,
        summary=paper.summary,
        themes=paper.themes or [],
        sentiment_score=paper.sentiment_score,
        complexity_score=paper.complexity_score
    )
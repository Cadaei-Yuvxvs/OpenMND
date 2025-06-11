from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ResearchPaper(Base):
    __tablename__ = "openmnd_research_papers"  # Updated table name

    id = Column(Integer, primary_key=True, index=True)
    pubmed_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(Text)
    authors = Column(JSON)  # List of author names
    journal = Column(String)
    publication_date = Column(DateTime)
    doi = Column(String)
    keywords = Column(JSON)  # List of keywords
    mesh_terms = Column(JSON)  # Medical Subject Headings
    citation_count = Column(Integer, default=0)

    # AI-generated fields
    summary = Column(Text)  # AI-generated summary
    themes = Column(JSON)  # Extracted themes
    sentiment_score = Column(Integer)  # Research optimism score
    complexity_score = Column(Integer)  # 1-10 complexity rating

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_processed = Column(Boolean, default=False)

class ResearchTheme(Base):
    __tablename__ = "openmnd_research_themes"  # Updated table name

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    paper_count = Column(Integer, default=0)
    trend_direction = Column(String)  # 'increasing', 'decreasing', 'stable'
    created_at = Column(DateTime, server_default=func.now())

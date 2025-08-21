from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class Keyword(BaseModel):
    keyword: str
    importance: str = Field(..., description="high, medium, or low")
    frequency: int
    present: Optional[bool] = None

class Issue(BaseModel):
    type: str = Field(..., description="critical, warning, or info")
    category: str
    title: str
    description: str
    suggestions: List[str] = []

class SectionAnalysis(BaseModel):
    present: bool
    score: int = Field(..., ge=0, le=100)
    issues: List[str] = []

class Recommendation(BaseModel):
    priority: str = Field(..., description="high, medium, or low")
    title: str
    description: str
    impact: str

class AnalysisRequest(BaseModel):
    job_description: Optional[str] = None

class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    overall_score: int = Field(..., ge=0, le=100)
    ats_compatibility: int = Field(..., ge=0, le=100)
    keyword_match: int = Field(..., ge=0, le=100)
    skills_match: int = Field(..., ge=0, le=100)
    format_score: int = Field(..., ge=0, le=100)
    issues: List[Issue]
    missing_keywords: List[Keyword]
    found_keywords: List[Keyword]
    sections: Dict[str, SectionAnalysis]
    recommendations: List[Recommendation]
    processing_time: Optional[float] = None
    job_description: Optional[str] = None

class KeywordAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

class KeywordAnalysisResult(BaseModel):
    missing_keywords: List[Keyword]
    found_keywords: List[Keyword]
    keyword_match: int = Field(..., ge=0, le=100)

class AnalysisHistory(BaseModel):
    analyses: List[AnalysisResult]
    total_count: int
    page: int = 1
    page_size: int = 10

# Database models for MongoDB
class AnalysisDocument(BaseModel):
    id: str = Field(alias="_id")
    file_name: str
    file_size: int
    upload_date: datetime
    original_text: str
    job_description: Optional[str] = None
    scores: Dict[str, int]
    analysis: Dict[str, Any]
    metadata: Dict[str, Any]

    class Config:
        populate_by_name = True
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import time
import logging
from datetime import datetime

from services.resume_parser import ResumeParser
from services.ats_analyzer import ATSAnalyzer
from services.file_handler import FileHandler
from models.analysis import (
    AnalysisResult, 
    KeywordAnalysisRequest, 
    KeywordAnalysisResult,
    AnalysisHistory,
    Issue,
    Keyword,
    SectionAnalysis,
    Recommendation
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])

# Initialize services
resume_parser = ResumeParser()
ats_analyzer = ATSAnalyzer()
file_handler = FileHandler()

@router.post("/analyze", response_model=dict)
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Upload and analyze a resume file for ATS compatibility
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        
        # Validate and save file
        try:
            file_handler.validate_file(file_content, file.filename, file.content_type)
            file_path, file_type = await file_handler.save_uploaded_file(
                file_content, file.filename, file.content_type
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Parse resume
        try:
            parsed_resume = resume_parser.parse_resume(file_path, file_type)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not parse resume: {str(e)}")
        
        # Analyze with ATS engine
        try:
            analysis = ats_analyzer.analyze_resume(parsed_resume, job_description)
        except Exception as e:
            logger.error(f"ATS analysis error: {str(e)}")
            raise HTTPException(status_code=500, detail="Analysis failed")
        
        processing_time = time.time() - start_time
        
        # Convert to response format
        result = AnalysisResult(
            file_name=file.filename,
            overall_score=analysis['overall_score'],
            ats_compatibility=analysis['ats_compatibility'],
            keyword_match=analysis['keyword_match'],
            skills_match=analysis['skills_match'],
            format_score=analysis['format_score'],
            issues=[Issue(**issue) for issue in analysis['issues']],
            missing_keywords=[Keyword(**kw) for kw in analysis['missing_keywords']],
            found_keywords=[Keyword(**kw) for kw in analysis['found_keywords']],
            sections={
                name: SectionAnalysis(**section) 
                for name, section in analysis['sections'].items()
            },
            recommendations=[Recommendation(**rec) for rec in analysis['recommendations']],
            processing_time=processing_time,
            job_description=job_description
        )
        
        # Save to database
        try:
            analysis_doc = {
                "_id": result.id,
                "file_name": result.file_name,
                "file_size": len(file_content),
                "upload_date": result.upload_date,
                "original_text": parsed_resume.get('raw_text', ''),
                "job_description": job_description,
                "scores": {
                    "overall": result.overall_score,
                    "ats_compatibility": result.ats_compatibility,
                    "keyword_match": result.keyword_match,
                    "skills_match": result.skills_match,
                    "format_score": result.format_score
                },
                "analysis": {
                    "issues": [issue.dict() for issue in result.issues],
                    "missing_keywords": [kw.dict() for kw in result.missing_keywords],
                    "found_keywords": [kw.dict() for kw in result.found_keywords],
                    "sections": {name: section.dict() for name, section in result.sections.items()},
                    "recommendations": [rec.dict() for rec in result.recommendations]
                },
                "metadata": {
                    "file_type": file_type,
                    "processing_time": processing_time,
                    "version": "1.0"
                }
            }
            
            await db.analyses.insert_one(analysis_doc)
            logger.info(f"Analysis saved to database: {result.id}")
            
        except Exception as e:
            logger.error(f"Database save error: {str(e)}")
            # Continue without failing the request
        
        # Clean up old files periodically
        file_handler.cleanup_old_files()
        
        return {
            "success": True,
            "data": result.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/keywords", response_model=dict)
async def analyze_keywords(request: KeywordAnalysisRequest):
    """
    Analyze keyword matching between resume text and job description
    """
    try:
        # Use ATS analyzer for keyword analysis
        keyword_analysis = ats_analyzer.analyze_keywords(
            request.resume_text, 
            request.job_description
        )
        
        result = KeywordAnalysisResult(
            missing_keywords=[Keyword(**kw) for kw in keyword_analysis['missing_keywords']],
            found_keywords=[Keyword(**kw) for kw in keyword_analysis['found_keywords']],
            keyword_match=keyword_analysis['match_percentage']
        )
        
        return {
            "success": True,
            "data": result.dict()
        }
        
    except Exception as e:
        logger.error(f"Keyword analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Keyword analysis failed")

@router.get("/history", response_model=dict)
async def get_analysis_history(
    page: int = 1,
    page_size: int = 10,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get analysis history with pagination
    """
    try:
        # Validate parameters
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        if page_size > 100:
            page_size = 100
            
        # Calculate skip value
        skip = (page - 1) * page_size
        
        # Get total count
        total_count = await db.analyses.count_documents({})
        
        # Get analyses with pagination
        cursor = db.analyses.find({}).sort("upload_date", -1).skip(skip).limit(page_size)
        analyses_docs = await cursor.to_list(length=page_size)
        
        # Convert to response format
        analyses = []
        for doc in analyses_docs:
            try:
                analysis = AnalysisResult(
                    id=doc["_id"],
                    file_name=doc["file_name"],
                    upload_date=doc["upload_date"],
                    overall_score=doc["scores"]["overall"],
                    ats_compatibility=doc["scores"]["ats_compatibility"],
                    keyword_match=doc["scores"]["keyword_match"],
                    skills_match=doc["scores"]["skills_match"],
                    format_score=doc["scores"]["format_score"],
                    issues=[Issue(**issue) for issue in doc["analysis"]["issues"]],
                    missing_keywords=[Keyword(**kw) for kw in doc["analysis"]["missing_keywords"]],
                    found_keywords=[Keyword(**kw) for kw in doc["analysis"]["found_keywords"]],
                    sections={
                        name: SectionAnalysis(**section) 
                        for name, section in doc["analysis"]["sections"].items()
                    },
                    recommendations=[Recommendation(**rec) for rec in doc["analysis"]["recommendations"]],
                    processing_time=doc["metadata"].get("processing_time"),
                    job_description=doc.get("job_description")
                )
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Error converting analysis doc: {str(e)}")
                continue
        
        result = AnalysisHistory(
            analyses=analyses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
        return {
            "success": True,
            "data": result.dict()
        }
        
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve history")

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a specific analysis
    """
    try:
        result = await db.analyses.delete_one({"_id": analysis_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "success": True,
            "message": "Analysis deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete analysis")
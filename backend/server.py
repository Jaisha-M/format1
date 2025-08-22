from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pathlib import Path
from typing import Optional
import logging

# Import our advanced services
from services.advanced_resume_parser import AdvancedResumeParser
from services.ats_scoring_engine import ATSScoringEngine

app = FastAPI(title="Bruwrite ATS Resume Checker", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_parser = AdvancedResumeParser()
scoring_engine = ATSScoringEngine()

logger = logging.getLogger(__name__)

def is_resume_content(text: str) -> bool:
    """Enhanced resume detection"""
    text_lower = text.lower()
    
    # Strong resume indicators
    resume_indicators = [
        'experience', 'education', 'skills', 'work', 'employment', 
        'resume', 'cv', 'curriculum vitae', 'objective', 'summary',
        'achievements', 'projects', 'certifications', 'qualifications',
        'professional', 'career', 'position', 'responsibilities'
    ]
    
    # Strong non-resume indicators
    non_resume_indicators = [
        'invoice', 'bill', 'payment', 'amount due', 'total amount',
        'due date', 'billing', 'account number', 'transaction',
        'receipt', 'purchase', 'order', 'refund', 'tax', 'electricity',
        'utility', 'statement', 'balance', 'charges', 'fee'
    ]
    
    resume_score = sum(1 for indicator in resume_indicators if indicator in text_lower)
    non_resume_score = sum(1 for indicator in non_resume_indicators if indicator in text_lower)
    
    # Enhanced detection logic
    word_count = len(text.split())
    
    # Must have at least 3 resume indicators, fewer non-resume indicators, and reasonable length
    is_resume = (
        resume_score >= 3 and 
        non_resume_score < resume_score and 
        word_count >= 100 and
        ('@' in text or 'email' in text_lower)  # Should have contact info
    )
    
    return is_resume

@app.get("/api/")
async def root():
    return {"message": "Bruwrite ATS Resume Checker API v2.0"}

@app.post("/api/analyze")
async def analyze_resume_comprehensive(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """Comprehensive resume analysis with proper ATS scoring"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload PDF, DOCX, DOC, or TXT files."
        )
    
    # Check file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    if len(content) < 100:
        raise HTTPException(status_code=400, detail="File appears to be empty or too small.")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Parse resume with advanced parser
        parsed_data = resume_parser.parse_resume(tmp_file_path, file_ext[1:])  # Remove dot from extension
        
        # Check if content is actually a resume
        if not is_resume_content(parsed_data['raw_text']):
            raise HTTPException(
                status_code=400,
                detail="The uploaded document does not appear to be a resume. Please upload a valid resume file containing work experience, education, and skills information."
            )
        
        # Calculate comprehensive ATS score
        scoring_result = scoring_engine.calculate_comprehensive_score(
            parsed_data, job_description, job_title
        )
        
        # Format response according to frontend expectations
        response = {
            # Overall scores
            'overall_score': scoring_result['overall_score'],
            'format_score': scoring_result['component_scores']['formatting_structure']['score'],
            'keyword_score': scoring_result['component_scores']['keywords_skills']['score'], 
            'skills_score': scoring_result['component_scores']['keywords_skills']['score'],  # Same as keyword for now
            'experience_score': scoring_result['component_scores']['work_experience']['score'],
            
            # Key metrics
            'total_keywords': parsed_data['skills']['total_skills_count'],
            'sections_count': sum(1 for section in parsed_data['sections'].values() if section.get('found', False)),
            'word_count': parsed_data['readability']['word_count'],
            'readability_score': int(parsed_data['readability']['readability_score']),
            
            # Issues (convert to expected format)
            'issues': [],
            
            # Recommendations
            'recommendations': [],
            
            # Job matching (if provided)
            'missing_keywords': []
        }
        
        # Convert issues to frontend format
        for weakness in scoring_result['weaknesses']:
            response['issues'].append({
                'severity': 'critical' if '❌' in weakness else 'warning',
                'title': weakness.replace('❌ ', '').replace('⚠️ ', '').split(' - ')[0],
                'description': weakness.replace('❌ ', '').replace('⚠️ ', '')
            })
        
        # Convert suggestions to frontend format
        for suggestion in scoring_result['suggestions']:
            response['recommendations'].append({
                'title': suggestion['title'],
                'description': suggestion['description'],
                'impact': suggestion['impact'].replace('+', '').replace(' points', '')
            })
        
        # Add job matching data if available
        if scoring_result.get('job_match_analysis'):
            job_match = scoring_result['job_match_analysis']
            response['missing_keywords'] = job_match.get('top_missing_keywords', [])
        
        # Add strengths as positive issues
        for strength in scoring_result['strengths']:
            response['issues'].append({
                'severity': 'info',
                'title': 'Strength Identified',
                'description': strength.replace('✅ ', '')
            })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}. Please ensure your file contains readable text and is a valid resume."
        )
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass
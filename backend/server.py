from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pathlib import Path
from typing import Optional
import logging

# Import our comprehensive services
from services.advanced_resume_parser import AdvancedResumeParser
from services.comprehensive_ats_analyzer import ComprehensiveATSAnalyzer

app = FastAPI(title="Bruwrite ATS Resume Checker", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
resume_parser = AdvancedResumeParser()
ats_analyzer = ComprehensiveATSAnalyzer()

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
    return {"message": "Bruwrite ATS Resume Checker API v3.0 - Comprehensive Analysis"}

@app.post("/api/analyze")
async def analyze_resume_comprehensive(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """Comprehensive ATS resume analysis with detailed checklist format"""
    
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
        
        # Perform comprehensive ATS analysis
        comprehensive_analysis = ats_analyzer.analyze_comprehensive(
            parsed_data, job_description, job_title
        )
        
        # Format response for frontend compatibility
        executive_summary = comprehensive_analysis['executive_summary']
        ats_scorecard = comprehensive_analysis['ats_scorecard']
        
        response = {
            # Executive Summary
            'overall_score': executive_summary['overall_ats_score'],
            'keyword_match': executive_summary['keyword_match'],
            'skills_match': executive_summary['skills_match'],
            'formatting_readability': executive_summary['formatting_readability'],
            'summary_statement': executive_summary['summary_statement'],
            
            # Detailed scores for frontend display
            'format_score': ats_scorecard['formatting_readability'],
            'keyword_score': ats_scorecard['keyword_match'],
            'skills_score': ats_scorecard['skills_match'],
            'experience_score': ats_scorecard['experience_relevance'],
            
            # Key metrics
            'total_keywords': len(comprehensive_analysis['detailed_analysis']['skills_section']['skills_found']['technical']) + 
                             len(comprehensive_analysis['detailed_analysis']['skills_section']['skills_found']['soft']),
            'sections_count': sum(1 for section in comprehensive_analysis['detailed_analysis'].values() 
                                if isinstance(section, dict) and section.get('score', 0) > 0),
            'word_count': len(parsed_data['raw_text'].split()),
            'readability_score': int(comprehensive_analysis['detailed_analysis']['formatting_readability']['score']),
            
            # Convert detailed analysis to frontend format
            'issues': [],
            'recommendations': comprehensive_analysis['final_recommendations'],
            'missing_keywords': comprehensive_analysis['detailed_analysis']['keywords_relevance'].get('missing_keywords', []),
            
            # Full analysis data for detailed view
            'comprehensive_analysis': comprehensive_analysis,
            'pie_chart_data': comprehensive_analysis['pie_chart_data']
        }
        
        # Convert detailed analysis to issues format
        detailed_analysis = comprehensive_analysis['detailed_analysis']
        
        for section_name, section_data in detailed_analysis.items():
            if isinstance(section_data, dict) and 'recommendations' in section_data:
                for rec in section_data['recommendations']:
                    severity = 'critical' if section_data.get('score', 100) < 50 else 'warning'
                    response['issues'].append({
                        'severity': severity,
                        'title': f"{section_name.replace('_', ' ').title()} Issue",
                        'description': rec
                    })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}", exc_info=True)
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
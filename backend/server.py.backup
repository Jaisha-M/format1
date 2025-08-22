from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import tempfile
from pathlib import Path
import PyMuPDF as fitz
from docx import Document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except:
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text).strip()
    except:
        return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except:
        return ""

def analyze_resume(text):
    """Simple resume analysis"""
    if not text or len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract meaningful text from resume")
    
    text_lower = text.lower()
    
    # Count words
    word_count = len(text.split())
    
    # Check for common resume sections
    sections = {
        'contact': any(keyword in text_lower for keyword in ['email', 'phone', '@', 'contact']),
        'experience': any(keyword in text_lower for keyword in ['experience', 'work', 'employment', 'job']),
        'education': any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college']),
        'skills': any(keyword in text_lower for keyword in ['skills', 'technologies', 'competencies'])
    }
    sections_found = sum(sections.values())
    
    # Check for keywords (common skills/terms)
    keywords = [
        'management', 'leadership', 'team', 'project', 'analysis', 'communication',
        'python', 'javascript', 'java', 'sql', 'excel', 'marketing', 'sales',
        'customer', 'service', 'development', 'design', 'strategy', 'planning'
    ]
    keywords_found = sum(1 for keyword in keywords if keyword in text_lower)
    
    # Calculate format score
    format_score = 70  # Base score
    if sections['contact']: format_score += 10
    if sections['experience']: format_score += 10
    if sections['education']: format_score += 5
    if sections['skills']: format_score += 5
    format_score = min(100, format_score)
    
    # Calculate overall score
    keyword_score = min(100, (keywords_found / len(keywords)) * 100)
    section_score = (sections_found / len(sections)) * 100
    word_score = 100 if 200 <= word_count <= 800 else 70
    
    overall_score = int((format_score * 0.3) + (keyword_score * 0.3) + (section_score * 0.2) + (word_score * 0.2))
    
    # Generate issues
    issues = []
    if word_count < 200:
        issues.append("Resume is too short. Add more details about your experience.")
    if word_count > 1000:
        issues.append("Resume is too long. Consider condensing the content.")
    if not sections['contact']:
        issues.append("Missing contact information section.")
    if not sections['experience']:
        issues.append("Missing work experience section.")
    if not sections['skills']:
        issues.append("Missing skills section.")
    if keywords_found < 5:
        issues.append("Resume lacks important keywords. Add more relevant skills and terms.")
    
    # Generate recommendations
    recommendations = []
    if overall_score < 70:
        recommendations.append("Consider reorganizing your resume with clear section headers.")
    if keyword_score < 50:
        recommendations.append("Add more industry-relevant keywords and skills.")
    if not sections['education']:
        recommendations.append("Add an education section if applicable.")
    recommendations.append("Use bullet points for better readability.")
    recommendations.append("Quantify your achievements with numbers and percentages.")
    if sections_found < 3:
        recommendations.append("Add standard resume sections: Contact, Experience, Education, Skills.")
    
    return {
        'overall_score': overall_score,
        'format_score': format_score,
        'keywords_found': keywords_found,
        'sections_found': sections_found,
        'word_count': word_count,
        'issues': issues,
        'recommendations': recommendations
    }

@app.get("/api/")
async def root():
    return {"message": "ATS Resume Checker API"}

@app.post("/api/analyze")
async def analyze_resume_file(file: UploadFile = File(...)):
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.doc', '.docx', '.txt']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOC, DOCX, or TXT files.")
    
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Extract text based on file type
        if file_ext == '.pdf':
            text = extract_text_from_pdf(tmp_file_path)
        elif file_ext == '.docx':
            text = extract_text_from_docx(tmp_file_path)
        elif file_ext == '.doc':
            # For .doc files, try to read as text (limited support)
            text = extract_text_from_txt(tmp_file_path)
        else:  # .txt
            text = extract_text_from_txt(tmp_file_path)
        
        # Analyze the text
        results = analyze_resume(text)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass
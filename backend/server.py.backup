from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import tempfile
from pathlib import Path
from typing import Optional, List, Dict
import string

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_txt(file_path):
    """Extract text from TXT files"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except:
        return ""

def simple_pdf_text_extract(file_path):
    """Simple PDF text extraction"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Try to decode and extract readable text
        try:
            text = content.decode('utf-8', errors='ignore')
        except:
            text = content.decode('latin1', errors='ignore')
        
        # Remove binary junk and keep only readable text
        readable_chars = string.printable
        text = ''.join(char for char in text if char in readable_chars)
        
        return text.strip()
    except:
        return ""

def is_resume_content(text: str) -> bool:
    """Check if the content appears to be a resume"""
    text_lower = text.lower()
    
    # Resume indicators
    resume_indicators = [
        'experience', 'education', 'skills', 'work', 'employment', 
        'resume', 'cv', 'curriculum vitae', 'objective', 'summary',
        'achievements', 'projects', 'certifications', 'qualifications'
    ]
    
    # Non-resume indicators (bills, invoices, etc.)
    non_resume_indicators = [
        'invoice', 'bill', 'payment', 'amount due', 'total amount',
        'due date', 'billing', 'account number', 'transaction',
        'receipt', 'purchase', 'order', 'refund', 'tax'
    ]
    
    resume_score = sum(1 for indicator in resume_indicators if indicator in text_lower)
    non_resume_score = sum(1 for indicator in non_resume_indicators if indicator in text_lower)
    
    # Must have at least 2 resume indicators and fewer non-resume indicators
    return resume_score >= 2 and non_resume_score < resume_score

def extract_contact_info(text: str) -> Dict:
    """Extract contact information"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        'has_email': len(emails) > 0,
        'has_phone': len(phones) > 0,
        'email_count': len(emails),
        'phone_count': len(phones)
    }

def analyze_sections(text: str) -> Dict:
    """Analyze resume sections"""
    text_lower = text.lower()
    
    sections = {
        'contact': any(keyword in text_lower for keyword in ['email', 'phone', '@', 'contact']),
        'summary': any(keyword in text_lower for keyword in ['summary', 'objective', 'profile', 'about']),
        'experience': any(keyword in text_lower for keyword in ['experience', 'work', 'employment', 'job', 'position']),
        'education': any(keyword in text_lower for keyword in ['education', 'degree', 'university', 'college', 'school']),
        'skills': any(keyword in text_lower for keyword in ['skills', 'technologies', 'competencies', 'technical']),
        'achievements': any(keyword in text_lower for keyword in ['achievements', 'accomplishments', 'awards', 'projects'])
    }
    
    return sections

def analyze_keywords(text: str, job_title: str = None, job_description: str = None) -> Dict:
    """Analyze keywords and skills"""
    text_lower = text.lower()
    
    # Technical skills
    tech_skills = [
        'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'html', 'css',
        'git', 'docker', 'aws', 'azure', 'mongodb', 'postgresql', 'mysql',
        'machine learning', 'data analysis', 'agile', 'scrum'
    ]
    
    # Soft skills
    soft_skills = [
        'leadership', 'management', 'communication', 'teamwork', 'problem solving',
        'analytical', 'creative', 'organized', 'detail oriented', 'collaborative'
    ]
    
    # Industry keywords
    industry_keywords = [
        'project management', 'customer service', 'sales', 'marketing', 'finance',
        'operations', 'strategy', 'business development', 'quality assurance'
    ]
    
    all_keywords = tech_skills + soft_skills + industry_keywords
    
    found_keywords = []
    missing_keywords = []
    
    for keyword in all_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # If job description provided, analyze against it
    if job_description:
        job_desc_lower = job_description.lower()
        job_keywords = []
        
        # Extract keywords from job description
        for keyword in all_keywords:
            if keyword in job_desc_lower and keyword not in found_keywords:
                missing_keywords.append(keyword)
            elif keyword in job_desc_lower and keyword in found_keywords:
                job_keywords.append(keyword)
    
    return {
        'found_keywords': found_keywords,
        'missing_keywords': missing_keywords[:10],  # Limit to top 10
        'total_found': len(found_keywords),
        'keyword_density': len(found_keywords) / max(len(text.split()), 1) * 100
    }

def analyze_experience(text: str) -> Dict:
    """Analyze work experience quality"""
    text_lower = text.lower()
    
    # Look for quantified achievements
    numbers_pattern = r'\b\d+%|\b\d+\s*(million|thousand|k\b|\$)'
    quantified_achievements = len(re.findall(numbers_pattern, text_lower))
    
    # Look for action verbs
    action_verbs = [
        'achieved', 'improved', 'increased', 'developed', 'managed', 'led',
        'created', 'implemented', 'designed', 'optimized', 'reduced', 'built'
    ]
    
    action_verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    
    # Look for job progression
    has_progression = any(title in text_lower for title in ['senior', 'lead', 'manager', 'director'])
    
    return {
        'quantified_achievements': quantified_achievements,
        'action_verbs': action_verb_count,
        'has_progression': has_progression
    }

def calculate_readability(text: str) -> int:
    """Simple readability score"""
    sentences = len(re.findall(r'[.!?]+', text))
    words = len(text.split())
    
    if sentences == 0:
        return 50
    
    avg_words_per_sentence = words / sentences
    
    # Ideal is 15-20 words per sentence
    if 15 <= avg_words_per_sentence <= 20:
        return 90
    elif 10 <= avg_words_per_sentence <= 25:
        return 75
    else:
        return 60

def analyze_resume_advanced(text: str, job_title: str = None, job_description: str = None) -> Dict:
    """Advanced resume analysis"""
    
    # Check if content is actually a resume
    if not is_resume_content(text):
        raise HTTPException(
            status_code=400, 
            detail="The uploaded document does not appear to be a resume. Please upload a valid resume file."
        )
    
    word_count = len(text.split())
    
    # Minimum word count for a resume
    if word_count < 100:
        raise HTTPException(
            status_code=400,
            detail="The document is too short to be a complete resume. Please upload a more detailed resume."
        )
    
    # Analyze different aspects
    contact_info = extract_contact_info(text)
    sections = analyze_sections(text)
    keywords_analysis = analyze_keywords(text, job_title, job_description)
    experience_analysis = analyze_experience(text)
    readability = calculate_readability(text)
    
    # Calculate individual scores
    format_score = calculate_format_score(sections, contact_info, word_count)
    keyword_score = calculate_keyword_score(keywords_analysis, job_description)
    skills_score = calculate_skills_score(keywords_analysis)
    experience_score = calculate_experience_score(experience_analysis, sections)
    
    # Overall score (weighted average)
    overall_score = int(
        (format_score * 0.25) + 
        (keyword_score * 0.25) + 
        (skills_score * 0.25) + 
        (experience_score * 0.25)
    )
    
    # Generate issues and recommendations
    issues = generate_issues(sections, contact_info, keywords_analysis, experience_analysis, word_count)
    recommendations = generate_recommendations(sections, keywords_analysis, experience_analysis, overall_score)
    
    return {
        'overall_score': overall_score,
        'format_score': format_score,
        'keyword_score': keyword_score,
        'skills_score': skills_score,
        'experience_score': experience_score,
        'total_keywords': keywords_analysis['total_found'],
        'sections_count': sum(sections.values()),
        'word_count': word_count,
        'readability_score': readability,
        'missing_keywords': keywords_analysis['missing_keywords'],
        'issues': issues,
        'recommendations': recommendations
    }

def calculate_format_score(sections: Dict, contact_info: Dict, word_count: int) -> int:
    """Calculate format and structure score"""
    score = 0
    
    # Section completeness (60 points max)
    section_weights = {
        'contact': 15,
        'experience': 15,
        'education': 10,
        'skills': 10,
        'summary': 5,
        'achievements': 5
    }
    
    for section, present in sections.items():
        if present and section in section_weights:
            score += section_weights[section]
    
    # Contact info (20 points max)
    if contact_info['has_email']:
        score += 10
    if contact_info['has_phone']:
        score += 10
    
    # Word count appropriateness (20 points max)
    if 300 <= word_count <= 800:
        score += 20
    elif 200 <= word_count < 300 or 800 < word_count <= 1200:
        score += 15
    elif word_count >= 200:
        score += 10
    
    return min(100, score)

def calculate_keyword_score(keywords_analysis: Dict, job_description: str) -> int:
    """Calculate keyword relevance score"""
    base_score = min(80, keywords_analysis['total_found'] * 4)
    
    # Bonus for job description matching
    if job_description and keywords_analysis['missing_keywords']:
        # Penalize for missing important keywords
        penalty = len(keywords_analysis['missing_keywords']) * 2
        base_score = max(20, base_score - penalty)
    
    return min(100, base_score)

def calculate_skills_score(keywords_analysis: Dict) -> int:
    """Calculate skills alignment score"""
    # Base score on number of relevant skills found
    skills_found = keywords_analysis['total_found']
    
    if skills_found >= 15:
        return 95
    elif skills_found >= 10:
        return 85
    elif skills_found >= 5:
        return 70
    elif skills_found >= 3:
        return 55
    else:
        return 30

def calculate_experience_score(experience_analysis: Dict, sections: Dict) -> int:
    """Calculate experience quality score"""
    score = 40  # Base score
    
    if sections.get('experience', False):
        score += 20
    
    # Bonus for quantified achievements
    score += min(20, experience_analysis['quantified_achievements'] * 5)
    
    # Bonus for action verbs
    score += min(15, experience_analysis['action_verbs'] * 2)
    
    # Bonus for career progression
    if experience_analysis['has_progression']:
        score += 5
    
    return min(100, score)

def generate_issues(sections: Dict, contact_info: Dict, keywords_analysis: Dict, 
                   experience_analysis: Dict, word_count: int) -> List[Dict]:
    """Generate issues based on analysis"""
    issues = []
    
    # Critical issues
    if not contact_info['has_email']:
        issues.append({
            'severity': 'critical',
            'title': 'Missing Email Address',
            'description': 'Your resume must include a professional email address for employers to contact you.'
        })
    
    if not sections.get('experience', False):
        issues.append({
            'severity': 'critical',
            'title': 'Missing Work Experience',
            'description': 'No work experience section detected. This is essential for most job applications.'
        })
    
    # Warning issues
    if not contact_info['has_phone']:
        issues.append({
            'severity': 'warning',
            'title': 'Missing Phone Number',
            'description': 'Adding a phone number provides employers another way to reach you.'
        })
    
    if not sections.get('skills', False):
        issues.append({
            'severity': 'warning',
            'title': 'Missing Skills Section',
            'description': 'A dedicated skills section helps ATS systems identify your qualifications.'
        })
    
    if word_count < 200:
        issues.append({
            'severity': 'warning',
            'title': 'Resume Too Short',
            'description': f'Your resume is only {word_count} words. Consider adding more details about your experience.'
        })
    
    if experience_analysis['quantified_achievements'] == 0:
        issues.append({
            'severity': 'warning',
            'title': 'No Quantified Achievements',
            'description': 'Include specific numbers, percentages, or metrics to demonstrate your impact.'
        })
    
    return issues

def generate_recommendations(sections: Dict, keywords_analysis: Dict, 
                           experience_analysis: Dict, overall_score: int) -> List[Dict]:
    """Generate improvement recommendations"""
    recommendations = []
    
    if not sections.get('summary', False):
        recommendations.append({
            'title': 'Add Professional Summary',
            'description': 'Include a 2-3 sentence summary at the top highlighting your key qualifications.',
            'impact': '5'
        })
    
    if keywords_analysis['total_found'] < 10:
        recommendations.append({
            'title': 'Increase Keyword Usage',
            'description': 'Add more industry-relevant keywords and skills throughout your resume.',
            'impact': '10'
        })
    
    if experience_analysis['action_verbs'] < 5:
        recommendations.append({
            'title': 'Use Strong Action Verbs',
            'description': 'Start bullet points with powerful action verbs like "achieved," "improved," "led."',
            'impact': '8'
        })
    
    if experience_analysis['quantified_achievements'] < 3:
        recommendations.append({
            'title': 'Quantify Your Achievements',
            'description': 'Add specific numbers, percentages, and metrics to demonstrate your impact.',
            'impact': '12'
        })
    
    if not sections.get('achievements', False):
        recommendations.append({
            'title': 'Highlight Key Achievements',
            'description': 'Create an achievements or projects section to showcase your best work.',
            'impact': '6'
        })
    
    if overall_score < 70:
        recommendations.append({
            'title': 'Improve Overall Structure',
            'description': 'Reorganize your resume with clear sections and consistent formatting.',
            'impact': '15'
        })
    
    return recommendations

@app.get("/api/")
async def root():
    return {"message": "Bruwrite ATS Resume Checker API"}

@app.post("/api/analyze")
async def analyze_resume_file(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.doc', '.docx', '.txt']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload PDF, DOC, DOCX, or TXT files."
        )
    
    # Check file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Extract text based on file type
        if file_ext == '.pdf':
            text = simple_pdf_text_extract(tmp_file_path)
        elif file_ext in ['.docx', '.doc']:
            text = extract_text_from_txt(tmp_file_path)  # Fallback method
        else:  # .txt
            text = extract_text_from_txt(tmp_file_path)
        
        # Analyze the text
        results = analyze_resume_advanced(text, job_title, job_description)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed. Please ensure your file contains readable text.")
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_file_path)
        except:
            pass
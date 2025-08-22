from typing import Dict, List, Tuple
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class ATSScoringEngine:
    def __init__(self):
        # Weight distribution as per requirements
        self.score_weights = {
            'keywords_skills': 0.40,  # 40%
            'formatting_structure': 0.20,  # 20%
            'work_experience': 0.20,  # 20%
            'education_certifications': 0.10,  # 10%
            'readability_grammar': 0.10  # 10%
        }
        
        # Industry-specific keywords
        self.industry_keywords = {
            'technology': [
                'software', 'development', 'programming', 'coding', 'algorithm',
                'database', 'api', 'framework', 'debugging', 'testing',
                'agile', 'scrum', 'devops', 'cloud', 'architecture'
            ],
            'marketing': [
                'campaign', 'branding', 'social media', 'content', 'analytics',
                'seo', 'sem', 'conversion', 'engagement', 'strategy'
            ],
            'finance': [
                'financial', 'analysis', 'modeling', 'risk', 'compliance',
                'reporting', 'budgeting', 'forecasting', 'accounting', 'audit'
            ],
            'healthcare': [
                'patient', 'clinical', 'medical', 'healthcare', 'treatment',
                'diagnosis', 'therapy', 'nursing', 'hospital', 'care'
            ],
            'sales': [
                'sales', 'revenue', 'client', 'customer', 'relationship',
                'negotiation', 'pipeline', 'quota', 'territory', 'crm'
            ]
        }

    def calculate_comprehensive_score(self, parsed_resume: Dict, job_description: str = None, job_title: str = None) -> Dict:
        """Calculate comprehensive ATS score"""
        
        # Individual component scores
        keywords_score = self.calculate_keywords_skills_score(parsed_resume, job_description, job_title)
        formatting_score = self.calculate_formatting_structure_score(parsed_resume)
        experience_score = self.calculate_work_experience_score(parsed_resume)
        education_score = self.calculate_education_certifications_score(parsed_resume)
        readability_score = self.calculate_readability_grammar_score(parsed_resume)
        
        # Calculate weighted overall score
        overall_score = (
            keywords_score['score'] * self.score_weights['keywords_skills'] +
            formatting_score['score'] * self.score_weights['formatting_structure'] +
            experience_score['score'] * self.score_weights['work_experience'] +
            education_score['score'] * self.score_weights['education_certifications'] +
            readability_score['score'] * self.score_weights['readability_grammar']
        )
        
        # Generate comprehensive analysis
        analysis = {
            'overall_score': int(overall_score),
            'component_scores': {
                'keywords_skills': keywords_score,
                'formatting_structure': formatting_score,
                'work_experience': experience_score,
                'education_certifications': education_score,
                'readability_grammar': readability_score
            },
            'strengths': self.identify_strengths(keywords_score, formatting_score, experience_score, education_score, readability_score),
            'weaknesses': self.identify_weaknesses(keywords_score, formatting_score, experience_score, education_score, readability_score),
            'suggestions': self.generate_suggestions(keywords_score, formatting_score, experience_score, education_score, readability_score),
            'job_match_analysis': self.analyze_job_match(parsed_resume, job_description, job_title) if job_description else None
        }
        
        return analysis

    def calculate_keywords_skills_score(self, parsed_resume: Dict, job_description: str = None, job_title: str = None) -> Dict:
        """Calculate Keywords & Skills Match Score (40% weight)"""
        skills_data = parsed_resume.get('skills', {})
        text = parsed_resume.get('raw_text', '').lower()
        
        base_score = 0
        details = {}
        
        # Base score from skills count
        tech_skills_count = skills_data.get('tech_skills_count', 0)
        soft_skills_count = skills_data.get('soft_skills_count', 0)
        total_skills = tech_skills_count + soft_skills_count
        
        # Score based on skills diversity and count
        if total_skills >= 15:
            base_score = 90
        elif total_skills >= 10:
            base_score = 75
        elif total_skills >= 5:
            base_score = 60
        elif total_skills >= 3:
            base_score = 45
        else:
            base_score = 25
        
        details['total_skills_found'] = total_skills
        details['technical_skills'] = tech_skills_count
        details['soft_skills'] = soft_skills_count
        
        # Job description matching
        if job_description:
            match_analysis = self.analyze_keyword_match(text, job_description)
            
            # Adjust score based on job description match
            match_percentage = match_analysis['match_percentage']
            if match_percentage >= 80:
                base_score = min(95, base_score + 10)
            elif match_percentage >= 60:
                base_score = min(90, base_score + 5)
            elif match_percentage < 40:
                base_score = max(20, base_score - 15)
            
            details['job_match_percentage'] = match_percentage
            details['missing_keywords'] = match_analysis['missing_keywords']
            details['found_keywords'] = match_analysis['found_keywords']
        
        # Industry relevance (if job title provided)
        if job_title:
            industry_score = self.calculate_industry_relevance(text, job_title)
            base_score = (base_score + industry_score) / 2
            details['industry_relevance'] = industry_score
        
        return {
            'score': int(base_score),
            'details': details,
            'category': 'Keywords & Skills Match'
        }

    def calculate_formatting_structure_score(self, parsed_resume: Dict) -> Dict:
        """Calculate Formatting & Structure Score (20% weight)"""
        formatting_info = parsed_resume.get('formatting_info', {})
        sections = parsed_resume.get('sections', {})
        contact_info = parsed_resume.get('contact_info', {})
        
        score = 70  # Base score
        details = {}
        issues = []
        
        # Check standard sections (30 points)
        required_sections = ['work_experience', 'education', 'skills']
        sections_found = sum(1 for section in required_sections if sections.get(section, {}).get('found', False))
        score += (sections_found / len(required_sections)) * 30
        details['sections_found'] = f"{sections_found}/{len(required_sections)} required sections"
        
        # Contact information (20 points)
        contact_score = 0
        if contact_info.get('has_email'):
            contact_score += 10
        if contact_info.get('has_phone'):
            contact_score += 5
        if contact_info.get('has_linkedin'):
            contact_score += 5
        score += contact_score
        details['contact_completeness'] = f"{contact_score}/20 points"
        
        # Formatting issues (-10 points each)
        formatting_issues = formatting_info.get('formatting_issues', [])
        score -= len(formatting_issues) * 10
        if formatting_issues:
            issues.extend(formatting_issues)
        
        # ATS-friendly formatting checks
        if formatting_info.get('has_tables'):
            score -= 15
            issues.append("Contains tables that may cause ATS parsing issues")
        
        if formatting_info.get('has_images'):
            score -= 10
            issues.append("Contains images which are not ATS-readable")
        
        # Bias-sensitive information check
        bias_issues = contact_info.get('bias_issues', [])
        if bias_issues:
            score -= 5
            issues.append(f"Contains potentially biased information: {', '.join(bias_issues)}")
        
        details['formatting_issues'] = issues
        
        return {
            'score': max(0, min(100, int(score))),
            'details': details,
            'category': 'Formatting & Structure'
        }

    def calculate_work_experience_score(self, parsed_resume: Dict) -> Dict:
        """Calculate Work Experience Relevance Score (20% weight)"""
        work_exp = parsed_resume.get('work_experience', {})
        sections = parsed_resume.get('sections', {})
        
        score = 0
        details = {}
        
        # Check if work experience section exists
        if not sections.get('work_experience', {}).get('found', False):
            return {
                'score': 10,
                'details': {'issue': 'No work experience section found'},
                'category': 'Work Experience'
            }
        
        score = 40  # Base score for having experience section
        
        # Quantified achievements (25 points)
        quantified = work_exp.get('quantified_achievements', 0)
        if quantified >= 5:
            score += 25
        elif quantified >= 3:
            score += 20
        elif quantified >= 1:
            score += 10
        details['quantified_achievements'] = quantified
        
        # Action verbs usage (20 points)
        action_verbs = work_exp.get('action_verbs_count', 0)
        if action_verbs >= 10:
            score += 20
        elif action_verbs >= 5:
            score += 15
        elif action_verbs >= 3:
            score += 10
        details['action_verbs_count'] = action_verbs
        
        # Chronological order (10 points)
        if work_exp.get('is_reverse_chronological', False):
            score += 10
        details['chronological_order'] = work_exp.get('is_reverse_chronological', False)
        
        # Job titles and company indicators (5 points)
        if work_exp.get('job_titles_found') and len(work_exp['job_titles_found']) > 0:
            score += 3
        if work_exp.get('company_indicators', 0) > 0:
            score += 2
        
        details['job_titles'] = len(work_exp.get('job_titles_found', []))
        details['company_mentions'] = work_exp.get('company_indicators', 0)
        
        return {
            'score': min(100, int(score)),
            'details': details,
            'category': 'Work Experience'
        }

    def calculate_education_certifications_score(self, parsed_resume: Dict) -> Dict:
        """Calculate Education & Certifications Score (10% weight)"""
        education = parsed_resume.get('education', {})
        certifications = parsed_resume.get('certifications', {})
        sections = parsed_resume.get('sections', {})
        
        score = 0
        details = {}
        
        # Education section (60 points)
        if sections.get('education', {}).get('found', False):
            score += 40
            
            if education.get('degrees_found'):
                score += 15
                details['degrees'] = len(education['degrees_found'])
            
            if education.get('institutions_mentioned'):
                score += 5
                details['institution_mentioned'] = True
            
        # Certifications (40 points)
        cert_count = certifications.get('certifications_count', 0)
        if cert_count >= 3:
            score += 40
        elif cert_count >= 1:
            score += 25
        
        details['certifications_count'] = cert_count
        details['certifications_found'] = certifications.get('certifications_found', [])
        
        return {
            'score': min(100, int(score)),
            'details': details,
            'category': 'Education & Certifications'
        }

    def calculate_readability_grammar_score(self, parsed_resume: Dict) -> Dict:
        """Calculate Readability & Grammar Score (10% weight)"""
        readability = parsed_resume.get('readability', {})
        grammar_issues = parsed_resume.get('grammar_issues', [])
        
        score = 70  # Base score
        details = {}
        
        # Readability score (50 points)
        flesch_score = readability.get('flesch_reading_ease', 50)
        if flesch_score >= 60:  # Easy to read
            score += 30
        elif flesch_score >= 30:  # Moderately difficult
            score += 20
        else:  # Difficult
            score += 10
        
        details['readability_score'] = flesch_score
        details['reading_level'] = readability.get('flesch_grade_level', 8)
        
        # Word count appropriateness (20 points)
        word_count = readability.get('word_count', 0)
        if 300 <= word_count <= 800:
            score += 20
        elif 200 <= word_count < 300 or 800 < word_count <= 1200:
            score += 15
        elif word_count >= 150:
            score += 10
        
        details['word_count'] = word_count
        
        # Grammar issues (-5 points each)
        score -= len(grammar_issues) * 5
        details['grammar_issues'] = grammar_issues
        
        # Sentence length
        avg_sentence_length = readability.get('avg_sentence_length', 15)
        if 15 <= avg_sentence_length <= 25:
            score += 10
        elif 10 <= avg_sentence_length < 15 or 25 < avg_sentence_length <= 35:
            score += 5
        
        details['avg_sentence_length'] = avg_sentence_length
        
        return {
            'score': max(0, min(100, int(score))),
            'details': details,
            'category': 'Readability & Grammar'
        }

    def analyze_keyword_match(self, resume_text: str, job_description: str) -> Dict:
        """Analyze keyword matching between resume and job description"""
        # Extract important keywords from job description
        job_keywords = self.extract_job_keywords(job_description)
        
        found_keywords = []
        missing_keywords = []
        
        resume_lower = resume_text.lower()
        
        for keyword, importance in job_keywords:
            if keyword.lower() in resume_lower:
                found_keywords.append({'keyword': keyword, 'importance': importance})
            else:
                missing_keywords.append({'keyword': keyword, 'importance': importance})
        
        # Calculate match percentage
        total_weight = sum(3 if imp == 'high' else 2 if imp == 'medium' else 1 for _, imp in job_keywords)
        found_weight = sum(3 if kw['importance'] == 'high' else 2 if kw['importance'] == 'medium' else 1 for kw in found_keywords)
        
        match_percentage = (found_weight / max(total_weight, 1)) * 100
        
        return {
            'match_percentage': match_percentage,
            'found_keywords': found_keywords[:15],  # Top 15
            'missing_keywords': missing_keywords[:10],  # Top 10 missing
            'total_keywords_analyzed': len(job_keywords)
        }

    def extract_job_keywords(self, job_description: str) -> List[Tuple[str, str]]:
        """Extract keywords from job description with importance ratings"""
        text_lower = job_description.lower()
        
        # High importance keywords
        high_importance = []
        medium_importance = []
        low_importance = []
        
        # Technical skills (high importance)
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'mongodb', 'postgresql', 'html', 'css', 'typescript'
        ]
        
        # Job-specific terms (high importance)
        job_terms = [
            'experience', 'years', 'senior', 'junior', 'lead', 'manager', 'director',
            'bachelor', 'master', 'degree', 'certification', 'agile', 'scrum'
        ]
        
        # Soft skills (medium importance)
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'organized', 'detail-oriented', 'time management'
        ]
        
        # Industry terms (medium importance)
        industry_terms = [
            'development', 'engineering', 'marketing', 'sales', 'finance', 'healthcare',
            'consulting', 'operations', 'strategy', 'business'
        ]
        
        # Check for keywords in job description
        for skill in tech_skills + job_terms:
            if skill in text_lower:
                high_importance.append((skill, 'high'))
        
        for skill in soft_skills + industry_terms:
            if skill in text_lower:
                medium_importance.append((skill, 'medium'))
        
        # Extract other important words (low importance)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        word_freq = Counter(words)
        common_words = ['the', 'and', 'for', 'with', 'you', 'will', 'our', 'this', 'that', 'are', 'have', 'been', 'work']
        
        for word, freq in word_freq.most_common(20):
            if word not in common_words and len(word) > 3:
                if not any(word in [kw[0] for kw in high_importance + medium_importance]):
                    low_importance.append((word, 'low'))
        
        return high_importance + medium_importance + low_importance[:10]

    def calculate_industry_relevance(self, resume_text: str, job_title: str) -> int:
        """Calculate industry relevance score"""
        # Determine industry from job title
        industry = self.detect_industry(job_title)
        
        if industry and industry in self.industry_keywords:
            keywords = self.industry_keywords[industry]
            found_keywords = sum(1 for keyword in keywords if keyword in resume_text)
            relevance_score = (found_keywords / len(keywords)) * 100
            return int(relevance_score)
        
        return 50  # Default score if industry can't be determined

    def detect_industry(self, job_title: str) -> str:
        """Detect industry from job title"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['engineer', 'developer', 'programmer', 'software', 'tech']):
            return 'technology'
        elif any(word in title_lower for word in ['marketing', 'brand', 'digital', 'content']):
            return 'marketing'
        elif any(word in title_lower for word in ['finance', 'financial', 'accounting', 'analyst']):
            return 'finance'
        elif any(word in title_lower for word in ['nurse', 'doctor', 'medical', 'healthcare']):
            return 'healthcare'
        elif any(word in title_lower for word in ['sales', 'account', 'business development']):
            return 'sales'
        
        return None

    def identify_strengths(self, keywords_score, formatting_score, experience_score, education_score, readability_score) -> List[str]:
        """Identify resume strengths"""
        strengths = []
        
        if keywords_score['score'] >= 80:
            strengths.append("✅ Excellent keyword optimization and skills alignment")
        elif keywords_score['score'] >= 60:
            strengths.append("✅ Good technical and soft skills representation")
        
        if formatting_score['score'] >= 80:
            strengths.append("✅ ATS-friendly formatting and structure")
        
        if experience_score['score'] >= 80:
            strengths.append("✅ Strong quantified achievements and action verbs")
        elif experience_score['score'] >= 60:
            strengths.append("✅ Good work experience presentation")
        
        if education_score['score'] >= 80:
            strengths.append("✅ Comprehensive education and certifications")
        
        if readability_score['score'] >= 80:
            strengths.append("✅ Excellent readability and grammar")
        
        return strengths

    def identify_weaknesses(self, keywords_score, formatting_score, experience_score, education_score, readability_score) -> List[str]:
        """Identify resume weaknesses"""
        weaknesses = []
        
        if keywords_score['score'] < 50:
            weaknesses.append("❌ Limited keyword optimization - add more relevant skills")
        
        if formatting_score['score'] < 50:
            weaknesses.append("❌ Poor ATS formatting - avoid tables, images, and complex layouts")
        
        if experience_score['score'] < 50:
            weaknesses.append("❌ Weak work experience section - add quantified achievements")
        
        if education_score['score'] < 40:
            weaknesses.append("❌ Missing education details - add degrees and certifications")
        
        if readability_score['score'] < 50:
            weaknesses.append("❌ Poor readability - improve sentence structure and grammar")
        
        return weaknesses

    def generate_suggestions(self, keywords_score, formatting_score, experience_score, education_score, readability_score) -> List[Dict]:
        """Generate actionable suggestions"""
        suggestions = []
        
        if keywords_score['score'] < 70:
            suggestions.append({
                'title': 'Improve Keyword Optimization',
                'description': 'Add more relevant technical and soft skills matching the job requirements',
                'impact': '+15-20 points',
                'priority': 'high'
            })
        
        if formatting_score['score'] < 70:
            suggestions.append({
                'title': 'Fix Formatting Issues',
                'description': 'Remove tables, images, and use ATS-friendly fonts (Arial, Calibri)',
                'impact': '+10-15 points',
                'priority': 'high'
            })
        
        if experience_score['score'] < 70:
            suggestions.append({
                'title': 'Quantify Achievements',
                'description': 'Add specific numbers, percentages, and metrics to demonstrate impact',
                'impact': '+12-18 points',
                'priority': 'high'
            })
        
        if education_score['score'] < 60:
            suggestions.append({
                'title': 'Add Education Details',
                'description': 'Include degrees, institutions, and relevant certifications',
                'impact': '+8-12 points',
                'priority': 'medium'
            })
        
        if readability_score['score'] < 60:
            suggestions.append({
                'title': 'Improve Readability',
                'description': 'Use shorter sentences, fix grammar issues, and improve flow',
                'impact': '+5-10 points',
                'priority': 'medium'
            })
        
        return suggestions

    def analyze_job_match(self, parsed_resume: Dict, job_description: str, job_title: str = None) -> Dict:
        """Analyze how well the resume matches the job requirements"""
        if not job_description:
            return None
        
        text = parsed_resume.get('raw_text', '').lower()
        keyword_match = self.analyze_keyword_match(text, job_description)
        
        # Industry relevance
        industry_match = 50
        if job_title:
            industry_match = self.calculate_industry_relevance(text, job_title)
        
        # Overall job match score
        job_match_score = (keyword_match['match_percentage'] + industry_match) / 2
        
        return {
            'overall_match_score': int(job_match_score),
            'keyword_match_percentage': keyword_match['match_percentage'],
            'industry_relevance': industry_match,
            'matched_requirements': len(keyword_match['found_keywords']),
            'missing_requirements': len(keyword_match['missing_keywords']),
            'top_missing_keywords': [kw['keyword'] for kw in keyword_match['missing_keywords'][:5]]
        }
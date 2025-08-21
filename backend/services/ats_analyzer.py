import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    pass  # Already downloaded in requirements setup

class ATSAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # ATS-friendly formatting rules
        self.format_rules = {
            'use_standard_fonts': True,
            'avoid_tables': True,
            'use_bullet_points': True,
            'standard_sections': True,
            'consistent_formatting': True
        }
        
        # Section importance weights for scoring
        self.section_weights = {
            'contact': 0.10,
            'summary': 0.15,
            'experience': 0.40,
            'education': 0.15,
            'skills': 0.15,
            'certifications': 0.05
        }
        
        # Common important keywords for different industries
        self.industry_keywords = {
            'technology': [
                'software', 'development', 'programming', 'coding', 'algorithm',
                'database', 'api', 'framework', 'debugging', 'testing',
                'agile', 'scrum', 'devops', 'cloud', 'architecture'
            ],
            'data_science': [
                'machine learning', 'data analysis', 'statistics', 'modeling',
                'python', 'r', 'sql', 'visualization', 'big data', 'analytics'
            ],
            'marketing': [
                'campaign', 'branding', 'social media', 'content', 'analytics',
                'seo', 'sem', 'conversion', 'engagement', 'strategy'
            ],
            'finance': [
                'financial', 'analysis', 'modeling', 'risk', 'compliance',
                'reporting', 'budgeting', 'forecasting', 'accounting', 'audit'
            ]
        }
    
    def analyze_resume(self, parsed_resume: Dict, job_description: str = None) -> Dict:
        """Main analysis function that returns comprehensive ATS analysis"""
        try:
            resume_text = parsed_resume.get('raw_text', '')
            
            # Core analyses
            format_score = self.analyze_format(parsed_resume)
            ats_compatibility = self.calculate_ats_compatibility(parsed_resume)
            sections_analysis = self.analyze_sections(parsed_resume)
            
            # Keyword analysis
            if job_description:
                keyword_analysis = self.analyze_keywords(resume_text, job_description)
            else:
                keyword_analysis = self.analyze_keywords_without_jd(resume_text)
            
            # Generate issues and recommendations
            issues = self.generate_issues(parsed_resume, keyword_analysis, format_score)
            recommendations = self.generate_recommendations(issues, keyword_analysis)
            
            # Calculate overall score
            overall_score = self.calculate_overall_score({
                'format_score': format_score,
                'ats_compatibility': ats_compatibility,
                'keyword_match': keyword_analysis.get('match_percentage', 50),
                'sections_score': sections_analysis.get('overall_score', 70)
            })
            
            return {
                'overall_score': overall_score,
                'ats_compatibility': ats_compatibility,
                'keyword_match': keyword_analysis.get('match_percentage', 50),
                'skills_match': keyword_analysis.get('skills_match', 60),
                'format_score': format_score,
                'issues': issues,
                'missing_keywords': keyword_analysis.get('missing_keywords', []),
                'found_keywords': keyword_analysis.get('found_keywords', []),
                'sections': sections_analysis.get('sections', {}),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error in ATS analysis: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def analyze_format(self, parsed_resume: Dict) -> int:
        """Analyze resume formatting for ATS compatibility"""
        score = 100
        issues = parsed_resume.get('formatting_issues', [])
        
        # Deduct points for formatting issues
        if 'Potential table formatting detected' in issues:
            score -= 15
        
        if 'Excessive special characters detected' in issues:
            score -= 10
        
        if 'Potential formatting issues with line breaks' in issues:
            score -= 10
        
        # Check for bullet points (good for ATS)
        if not parsed_resume.get('has_bullet_points', False):
            score -= 15
        
        # Check word count (too short or too long can be issues)
        word_count = parsed_resume.get('word_count', 0)
        if word_count < 200:
            score -= 20
        elif word_count > 1000:
            score -= 10
        
        return max(0, min(100, score))
    
    def calculate_ats_compatibility(self, parsed_resume: Dict) -> int:
        """Calculate how well the resume would perform in ATS systems"""
        score = 80  # Base score
        
        # Check for contact information
        contact = parsed_resume.get('contact_info', {})
        if not contact.get('email'):
            score -= 20
        if not contact.get('phone'):
            score -= 10
        
        # Check for standard sections
        sections = parsed_resume.get('sections', {})
        required_sections = ['experience', 'education']
        for section in required_sections:
            if not sections.get(section, {}).get('present', False):
                score -= 15
        
        # Bonus for having skills section
        if sections.get('skills', {}).get('present', False):
            score += 10
        
        return max(0, min(100, score))
    
    def analyze_sections(self, parsed_resume: Dict) -> Dict:
        """Analyze individual resume sections"""
        sections = parsed_resume.get('sections', {})
        section_analysis = {}
        total_score = 0
        
        for section_name, section_data in sections.items():
            if section_data.get('present', False):
                # Basic score for having the section
                score = 70
                issues = []
                
                # Check content quality
                content = section_data.get('content', [])
                if len(content) < 2:
                    score -= 20
                    issues.append(f"Add more content to {section_name} section")
                
                # Special checks for experience section
                if section_name == 'experience':
                    if not any('year' in ' '.join(content).lower() or 
                             any(str(year) in ' '.join(content) for year in range(2010, 2025)) 
                             for content in [content]):
                        score -= 15
                        issues.append("Add dates to work experience")
                
                section_analysis[section_name] = {
                    'present': True,
                    'score': max(0, min(100, score)),
                    'issues': issues
                }
                total_score += score * self.section_weights.get(section_name, 0.1)
            else:
                section_analysis[section_name] = {
                    'present': False,
                    'score': 0,
                    'issues': [f"Add {section_name} section to resume"]
                }
        
        return {
            'sections': section_analysis,
            'overall_score': min(100, total_score)
        }
    
    def analyze_keywords(self, resume_text: str, job_description: str) -> Dict:
        """Analyze keyword matching between resume and job description"""
        try:
            # Extract keywords from job description
            jd_keywords = self.extract_keywords(job_description)
            resume_keywords = self.extract_keywords(resume_text)
            
            # Find matches
            found_keywords = []
            missing_keywords = []
            
            for keyword in jd_keywords[:20]:  # Top 20 keywords
                if any(kw.lower() in resume_text.lower() for kw in [keyword]):
                    found_keywords.append({
                        'keyword': keyword,
                        'importance': 'high' if keyword in jd_keywords[:5] else 'medium',
                        'frequency': resume_text.lower().count(keyword.lower()),
                        'present': True
                    })
                else:
                    missing_keywords.append({
                        'keyword': keyword,
                        'importance': 'high' if keyword in jd_keywords[:5] else 'medium',
                        'frequency': job_description.lower().count(keyword.lower())
                    })
            
            # Calculate match percentage
            match_percentage = (len(found_keywords) / max(len(jd_keywords[:20]), 1)) * 100
            
            return {
                'match_percentage': int(match_percentage),
                'skills_match': self.calculate_skills_match(resume_text, job_description),
                'found_keywords': found_keywords,
                'missing_keywords': missing_keywords
            }
            
        except Exception as e:
            logger.error(f"Error in keyword analysis: {str(e)}")
            return self.analyze_keywords_without_jd(resume_text)
    
    def analyze_keywords_without_jd(self, resume_text: str) -> Dict:
        """Analyze resume keywords without job description"""
        # Use general tech keywords for analysis
        general_keywords = [
            'management', 'leadership', 'team', 'project', 'analysis',
            'development', 'strategy', 'communication', 'problem-solving'
        ]
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in general_keywords:
            if keyword.lower() in resume_text.lower():
                found_keywords.append({
                    'keyword': keyword,
                    'importance': 'medium',
                    'frequency': resume_text.lower().count(keyword.lower()),
                    'present': True
                })
            else:
                missing_keywords.append({
                    'keyword': keyword,
                    'importance': 'medium',
                    'frequency': 1
                })
        
        match_percentage = (len(found_keywords) / len(general_keywords)) * 100
        
        return {
            'match_percentage': int(match_percentage),
            'skills_match': 60,  # Default score
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords[:5]  # Limit missing keywords
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        try:
            # Tokenize and clean
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
            
            # Use TF-IDF to find important terms
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                # If too few sentences, use simple frequency
                from collections import Counter
                word_freq = Counter(tokens)
                return [word for word, freq in word_freq.most_common(20)]
            
            vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            scores = np.mean(tfidf_matrix.toarray(), axis=0)
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores if score > 0.1]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            # Fallback to simple word frequency
            from collections import Counter
            tokens = word_tokenize(text.lower())
            tokens = [token for token in tokens if token.isalnum() and len(token) > 3]
            word_freq = Counter(tokens)
            return [word for word, freq in word_freq.most_common(20)]
    
    def calculate_skills_match(self, resume_text: str, job_description: str) -> int:
        """Calculate how well skills match between resume and job description"""
        try:
            # Simple cosine similarity between texts
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return int(similarity * 100)
        except:
            return 60  # Default score
    
    def calculate_overall_score(self, scores: Dict) -> int:
        """Calculate weighted overall ATS score"""
        weights = {
            'format_score': 0.25,
            'ats_compatibility': 0.25,
            'keyword_match': 0.30,
            'sections_score': 0.20
        }
        
        total_score = 0
        for metric, score in scores.items():
            weight = weights.get(metric, 0.25)
            total_score += score * weight
        
        return int(min(100, max(0, total_score)))
    
    def generate_issues(self, parsed_resume: Dict, keyword_analysis: Dict, format_score: int) -> List[Dict]:
        """Generate issues based on analysis results"""
        issues = []
        
        # Format issues
        if format_score < 80:
            issues.append({
                'type': 'warning',
                'category': 'Formatting',
                'title': 'Formatting needs improvement',
                'description': 'Your resume has formatting issues that may affect ATS parsing',
                'suggestions': [
                    'Use standard fonts like Arial or Calibri',
                    'Avoid tables and complex layouts',
                    'Use bullet points for better readability',
                    'Ensure consistent formatting throughout'
                ]
            })
        
        # Missing keywords
        missing_kw = keyword_analysis.get('missing_keywords', [])
        if len(missing_kw) > 3:
            issues.append({
                'type': 'critical',
                'category': 'Keywords',
                'title': 'Missing important keywords',
                'description': f'Your resume is missing {len(missing_kw)} important keywords',
                'suggestions': [
                    f'Add "{kw["keyword"]}" to relevant sections' for kw in missing_kw[:3]
                ]
            })
        
        # Section issues
        sections = parsed_resume.get('sections', {})
        if not sections.get('skills', {}).get('present', False):
            issues.append({
                'type': 'info',
                'category': 'Structure',
                'title': 'Add skills section',
                'description': 'A dedicated skills section can improve ATS parsing',
                'suggestions': [
                    'Create a skills section with relevant technical skills',
                    'Include both hard and soft skills',
                    'Use keywords from the job description'
                ]
            })
        
        return issues
    
    def generate_recommendations(self, issues: List[Dict], keyword_analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # High priority recommendations
        missing_kw = keyword_analysis.get('missing_keywords', [])
        if missing_kw:
            recommendations.append({
                'priority': 'high',
                'title': 'Add Missing Keywords',
                'description': f'Include the top {min(5, len(missing_kw))} missing keywords in relevant sections',
                'impact': '+15 points'
            })
        
        # Format recommendations
        critical_issues = [issue for issue in issues if issue['type'] == 'critical']
        if critical_issues:
            recommendations.append({
                'priority': 'high',
                'title': 'Fix Critical Issues',
                'description': 'Address formatting and structural problems that significantly impact ATS parsing',
                'impact': '+20 points'
            })
        
        # General improvements
        recommendations.append({
            'priority': 'medium',
            'title': 'Quantify Achievements',
            'description': 'Add specific numbers and percentages to your accomplishments',
            'impact': '+10 points'
        })
        
        recommendations.append({
            'priority': 'low',
            'title': 'Optimize Section Order',
            'description': 'Ensure sections are in a logical order: Contact, Summary, Experience, Education, Skills',
            'impact': '+5 points'
        })
        
        return recommendations
import re
import nltk
from collections import Counter
from typing import Dict, List, Tuple, Optional
import logging
import textstat
from datetime import datetime

logger = logging.getLogger(__name__)

class ComprehensiveATSAnalyzer:
    def __init__(self):
        # Standard sections expected in resumes
        self.standard_sections = {
            'contact': ['contact', 'personal information'],
            'headline': ['headline', 'objective', 'summary', 'professional summary', 'career objective'],
            'skills': ['skills', 'technical skills', 'core competencies', 'technologies', 'expertise'],  
            'experience': ['work experience', 'professional experience', 'experience', 'employment', 'career history'],
            'education': ['education', 'academic background', 'qualifications'],
            'certifications': ['certifications', 'certificates', 'licenses', 'credentials'],
            'projects': ['projects', 'achievements', 'accomplishments', 'portfolio'],
            'volunteer': ['volunteer', 'volunteer experience', 'community service']
        }
        
        # Action verbs for experience analysis
        self.action_verbs = [
            'achieved', 'accomplished', 'administered', 'analyzed', 'built', 'collaborated',
            'created', 'delivered', 'developed', 'directed', 'enhanced', 'established',
            'executed', 'facilitated', 'generated', 'implemented', 'improved', 'increased',
            'initiated', 'launched', 'led', 'managed', 'optimized', 'organized', 'performed',
            'planned', 'produced', 'reduced', 'resolved', 'streamlined', 'supervised',
            'transformed', 'utilized', 'coordinated', 'maintained', 'designed', 'conducted'
        ]
        
        # Industry skills database
        self.skill_categories = {
            'technical': {
                'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin', 'swift'],
                'web': ['html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express.js', 'django', 'flask', 'laravel', 'spring boot'],
                'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite', 'cassandra'],
                'cloud': ['aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
                'tools': ['git', 'jira', 'confluence', 'tableau', 'power bi', 'excel', 'photoshop', 'figma', 'sketch']
            },
            'soft': [
                'leadership', 'management', 'communication', 'teamwork', 'collaboration',
                'problem solving', 'analytical thinking', 'creative', 'organized', 'adaptable',
                'detail-oriented', 'time management', 'critical thinking', 'negotiation',
                'presentation', 'customer service', 'project management', 'strategic planning'
            ]
        }
        
        # Professional certifications
        self.certifications = [
            'pmp', 'project management professional', 'aws certified', 'azure certified', 'google certified',
            'cissp', 'cisa', 'cism', 'comptia', 'cisco certified', 'microsoft certified',
            'salesforce certified', 'scrum master', 'csm', 'six sigma', 'itil', 'cfa', 'cpa'
        ]
        
        # ATS-friendly fonts
        self.ats_fonts = ['arial', 'calibri', 'times new roman', 'helvetica', 'georgia', 'trebuchet ms', 'verdana']

    def analyze_comprehensive(self, parsed_resume: Dict, job_description: str = None, job_title: str = None) -> Dict:
        """Comprehensive ATS analysis following the detailed checklist"""
        
        try:
            text = parsed_resume.get('raw_text', '')
            if not text:
                raise ValueError("No text content found in resume")
            
            # Extract all required analysis components
            contact_analysis = self.analyze_contact_information(text)
            headline_analysis = self.analyze_headline_summary(text)
            skills_analysis = self.analyze_skills_section(text, job_description)
            experience_analysis = self.analyze_work_experience(text, job_description)
            education_analysis = self.analyze_education(text)
            certifications_analysis = self.analyze_certifications(text, job_description)
            projects_analysis = self.analyze_projects_achievements(text)
            keywords_analysis = self.analyze_keywords_relevance(text, job_description, job_title)
            formatting_analysis = self.analyze_formatting_readability(text, parsed_resume.get('formatting_info', {}))
            
            # Calculate component scores
            scores = self.calculate_component_scores(
                contact_analysis, headline_analysis, skills_analysis, experience_analysis,
                education_analysis, certifications_analysis, projects_analysis, 
                keywords_analysis, formatting_analysis
            )
            
            # Generate executive summary
            executive_summary = self.generate_executive_summary(scores, keywords_analysis)
            
            # Generate final recommendations
            final_recommendations = self.generate_final_recommendations(
                contact_analysis, headline_analysis, skills_analysis, experience_analysis,
                education_analysis, certifications_analysis, formatting_analysis, keywords_analysis
            )
            
            # Prepare pie chart data
            pie_chart_data = self.prepare_pie_chart_data(scores)
            
            return {
                'executive_summary': executive_summary,
                'detailed_analysis': {
                    'contact_information': contact_analysis,
                    'headline_summary': headline_analysis,
                    'skills_section': skills_analysis,
                    'work_experience': experience_analysis,
                    'education': education_analysis,
                    'certifications': certifications_analysis,
                    'projects_achievements': projects_analysis,
                    'keywords_relevance': keywords_analysis,
                    'formatting_readability': formatting_analysis
                },
                'ats_scorecard': scores,
                'pie_chart_data': pie_chart_data,
                'final_recommendations': final_recommendations
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis error: {str(e)}")
            raise e

    def analyze_contact_information(self, text: str) -> Dict:
        """Analyze contact information section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'recommendations': []
        }
        
        # Check for name (usually in first few lines)
        lines = text.split('\n')[:5]
        has_name = any(len(line.strip().split()) >= 2 and 
                      not '@' in line and not any(char.isdigit() for char in line) 
                      for line in lines if line.strip())
        analysis['checklist']['name_plain_text'] = has_name
        
        # Check for phone number
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        has_phone = bool(re.search(phone_pattern, text))
        analysis['checklist']['phone_number'] = has_phone
        
        # Check for professional email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        has_professional_email = bool(emails)
        analysis['checklist']['professional_email'] = has_professional_email
        
        # Check for location
        location_keywords = ['city', 'state', 'location', 'address', 'remote', 'relocation']
        has_location = any(keyword in text.lower() for keyword in location_keywords) or \
                      bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', text))  # City, ST format
        analysis['checklist']['location'] = has_location
        
        # Check for LinkedIn/portfolio
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        portfolio_patterns = ['github.com', 'portfolio', 'website', 'https://', 'http://']
        has_linkedin = bool(re.search(linkedin_pattern, text, re.IGNORECASE))
        has_portfolio = any(pattern in text.lower() for pattern in portfolio_patterns)
        analysis['checklist']['linkedin_portfolio'] = has_linkedin or has_portfolio
        
        # Check for header/footer issues (heuristic)
        lines = text.split('\n')
        first_line_contact = any(pattern in lines[0].lower() if lines else False 
                               for pattern in ['phone', 'email', '@', 'linkedin'])
        analysis['checklist']['no_header_footer'] = not first_line_contact
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_name:
            analysis['recommendations'].append("Add your full name at the top of the resume in plain text")
        if not has_phone:
            analysis['recommendations'].append("Include a phone number in international format")
        if not has_professional_email:
            analysis['recommendations'].append("Add a professional email address (avoid casual usernames)")
        if not has_location:
            analysis['recommendations'].append("Include your location (City, State) or 'Open to Relocation'")
        if not (has_linkedin or has_portfolio):
            analysis['recommendations'].append("Add LinkedIn profile or portfolio link to improve recruiter visibility")
        
        return analysis

    def analyze_headline_summary(self, text: str) -> Dict:
        """Analyze headline/objective/summary section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'recommendations': []
        }
        
        lines = text.split('\n')
        
        # Look for headline (usually after name, before main content)
        headline_indicators = ['summary', 'objective', 'profile', 'professional summary', 'career objective']
        has_headline_section = any(indicator in text.lower() for indicator in headline_indicators)
        
        # Check for clear headline/title
        potential_headlines = []
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line_clean = line.strip()
            if line_clean and not '@' in line_clean and not any(char.isdigit() for char in line_clean[:5]):
                if len(line_clean.split()) <= 6 and i > 0:  # Likely a title/headline
                    potential_headlines.append(line_clean)
        
        has_clear_headline = len(potential_headlines) > 0
        analysis['checklist']['clear_headline'] = has_clear_headline
        
        # Check summary length (3-4 lines)
        summary_text = ""
        if has_headline_section:
            # Extract text after summary indicators
            for indicator in headline_indicators:
                if indicator in text.lower():
                    start_idx = text.lower().find(indicator)
                    # Get next few lines
                    remaining_text = text[start_idx:]
                    summary_lines = remaining_text.split('\n')[1:5]  # Next 4 lines
                    summary_text = '\n'.join(summary_lines)
                    break
        
        summary_line_count = len([line for line in summary_text.split('\n') if line.strip()])
        has_appropriate_length = 2 <= summary_line_count <= 5
        analysis['checklist']['summary_length'] = has_appropriate_length
        
        # Check for role-specific keywords
        common_keywords = ['experience', 'skilled', 'expertise', 'specialist', 'professional', 'manager', 'developer', 'analyst']
        has_keywords = any(keyword in text.lower() for keyword in common_keywords)
        analysis['checklist']['role_keywords'] = has_keywords
        
        # Check for measurable language
        measurable_patterns = [r'\d+\+?\s*years?', r'\d+%', r'\$\d+', r'\d+\s*(million|thousand|k\b)', r'increased?.*\d+', r'improved?.*\d+']
        has_measurable = any(re.search(pattern, text, re.IGNORECASE) for pattern in measurable_patterns)
        analysis['checklist']['measurable_language'] = has_measurable
        
        # Check for generic phrases
        generic_phrases = ['hard working', 'hardworking', 'team player', 'detail oriented', 'motivated', 'passionate']
        has_generic = any(phrase in text.lower() for phrase in generic_phrases)
        analysis['checklist']['avoid_generic'] = not has_generic
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_clear_headline:
            analysis['recommendations'].append("Add a clear headline with your job title or specialization")
        if not has_headline_section or not has_appropriate_length:
            analysis['recommendations'].append("Include a 3-4 line professional summary with key qualifications")
        if not has_keywords:
            analysis['recommendations'].append("Include role-specific keywords in your summary")
        if not has_measurable:
            analysis['recommendations'].append("Add quantifiable achievements (e.g., 'Increased efficiency by 20%')")
        if has_generic:
            analysis['recommendations'].append("Remove generic phrases and replace with specific accomplishments")
        
        return analysis

    def analyze_skills_section(self, text: str, job_description: str = None) -> Dict:
        """Analyze skills section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'skills_found': {'technical': [], 'soft': []},
            'job_match_percentage': 0,
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Check for dedicated skills section
        skills_indicators = ['skills', 'technical skills', 'core competencies', 'technologies', 'expertise']
        has_skills_section = any(indicator in text_lower for indicator in skills_indicators)
        analysis['checklist']['dedicated_section'] = has_skills_section
        
        # Extract technical skills
        technical_skills = []
        for category, skills_list in self.skill_categories['technical'].items():
            for skill in skills_list:
                if skill in text_lower:
                    technical_skills.append(skill)
        
        # Extract soft skills
        soft_skills = []
        for skill in self.skill_categories['soft']:
            if skill in text_lower:
                soft_skills.append(skill)
        
        analysis['skills_found']['technical'] = technical_skills
        analysis['skills_found']['soft'] = soft_skills
        
        total_skills = len(technical_skills) + len(soft_skills)
        
        # Check skill balance
        has_balance = len(technical_skills) > 0 and len(soft_skills) > 0
        analysis['checklist']['skill_balance'] = has_balance
        
        # Check skill count (10-15 optimal)
        appropriate_count = 8 <= total_skills <= 20
        analysis['checklist']['appropriate_count'] = appropriate_count
        
        # Job description matching if provided
        if job_description:
            jd_lower = job_description.lower()
            
            # Extract skills from job description
            jd_technical = []
            jd_soft = []
            
            for category, skills_list in self.skill_categories['technical'].items():
                for skill in skills_list:
                    if skill in jd_lower:
                        jd_technical.append(skill)
            
            for skill in self.skill_categories['soft']:
                if skill in jd_lower:
                    jd_soft.append(skill)
            
            total_jd_skills = len(jd_technical) + len(jd_soft)
            matched_skills = len(set(technical_skills) & set(jd_technical)) + len(set(soft_skills) & set(jd_soft))
            
            if total_jd_skills > 0:
                analysis['job_match_percentage'] = (matched_skills / total_jd_skills) * 100
            
            analysis['checklist']['job_keywords'] = analysis['job_match_percentage'] > 50
        else:
            analysis['checklist']['job_keywords'] = True  # Default to true if no JD
        
        # Check for overstuffing
        skill_mentions = sum(text_lower.count(skill) for skill in technical_skills + soft_skills)
        word_count = len(text.split())
        skill_density = (skill_mentions / word_count) * 100 if word_count > 0 else 0
        no_overstuffing = skill_density < 15  # Less than 15% skill density
        analysis['checklist']['no_overstuffing'] = no_overstuffing
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_skills_section:
            analysis['recommendations'].append("Create a dedicated Skills section")
        if not has_balance:
            analysis['recommendations'].append("Include both technical and soft skills")
        if not appropriate_count:
            analysis['recommendations'].append("Include 10-15 relevant skills (currently have {})".format(total_skills))
        if job_description and analysis['job_match_percentage'] < 60:
            analysis['recommendations'].append("Add missing skills from job description such as: {}".format(
                ', '.join(list(set(jd_technical + jd_soft) - set(technical_skills + soft_skills))[:3])
            ))
        if not no_overstuffing:
            analysis['recommendations'].append("Reduce keyword stuffing - use skills naturally throughout resume")
        
        return analysis

    def analyze_work_experience(self, text: str, job_description: str = None) -> Dict:
        """Analyze work experience section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'quantifiable_impact_percentage': 0,
            'recommendations': []
        }
        
        # Check for reverse chronological order
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        is_reverse_chronological = len(years) >= 2 and all(int(years[i]) >= int(years[i+1]) for i in range(len(years)-1))
        analysis['checklist']['reverse_chronological'] = is_reverse_chronological or len(years) < 2
        
        # Check for required components
        has_job_titles = bool(re.search(r'\b(manager|director|engineer|analyst|specialist|coordinator|assistant|supervisor|lead|senior|junior)\b', text, re.IGNORECASE))
        analysis['checklist']['job_titles'] = has_job_titles
        
        has_companies = bool(re.search(r'\b(inc|llc|corp|company|ltd|organization|university|hospital)\b', text, re.IGNORECASE))
        analysis['checklist']['company_names'] = has_companies
        
        has_locations = bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', text))
        analysis['checklist']['locations'] = has_locations
        
        has_dates = len(years) > 0
        analysis['checklist']['dates'] = has_dates
        
        # Check date formatting consistency
        date_formats = re.findall(r'\b\d{1,2}/\d{4}|\b\d{4}[-–]\d{4}|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}', text, re.IGNORECASE)
        consistent_dates = len(set(type(d) for d in date_formats)) <= 2 if date_formats else False
        analysis['checklist']['consistent_dates'] = consistent_dates or len(date_formats) == 0
        
        # Check for bullet points
        bullet_patterns = [r'•', r'●', r'▪', r'-\s', r'\*\s']
        has_bullets = any(re.search(pattern, text) for pattern in bullet_patterns)
        analysis['checklist']['bullet_points'] = has_bullets
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.action_verbs if verb in text.lower())
        has_action_verbs = action_verb_count >= 5
        analysis['checklist']['action_verbs'] = has_action_verbs
        
        # Check for quantifiable achievements
        quantifiable_patterns = [
            r'\b\d+%', r'\$\d+', r'\b\d+\s*(million|thousand|k\b)', 
            r'\b\d+\+?\s*(people|employees|team|members)',
            r'increased?.*\d+', r'decreased?.*\d+', r'improved?.*\d+', r'reduced?.*\d+',
            r'achieved?.*\d+', r'generated?.*\d+', r'saved?.*\d+'
        ]
        quantifiable_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in quantifiable_patterns)
        total_bullets = len(re.findall(r'[•●▪*-]\s', text))
        
        if total_bullets > 0:
            analysis['quantifiable_impact_percentage'] = (quantifiable_matches / total_bullets) * 100
        
        has_quantifiable = analysis['quantifiable_impact_percentage'] > 30
        analysis['checklist']['quantifiable_achievements'] = has_quantifiable
        
        # Check for role-specific keywords
        if job_description:
            jd_words = set(re.findall(r'\b\w{4,}\b', job_description.lower()))
            resume_words = set(re.findall(r'\b\w{4,}\b', text.lower()))
            keyword_overlap = len(jd_words & resume_words) / len(jd_words) if jd_words else 0
            has_keywords = keyword_overlap > 0.2
        else:
            has_keywords = True  # Default if no JD
        
        analysis['checklist']['role_keywords'] = has_keywords
        
        # Check formatting issues
        has_no_paragraphs = '\n\n' not in text or text.count('\n\n') < text.count('\n') * 0.1
        analysis['checklist']['no_paragraphs'] = has_no_paragraphs
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not is_reverse_chronological and len(years) >= 2:
            analysis['recommendations'].append("Organize work experience in reverse chronological order")
        if not has_job_titles:
            analysis['recommendations'].append("Include clear job titles for each position")
        if not has_companies:
            analysis['recommendations'].append("Add company names and locations for each role")
        if not has_dates:
            analysis['recommendations'].append("Include employment dates in consistent format (MM/YYYY)")
        if not has_bullets:
            analysis['recommendations'].append("Use bullet points instead of paragraphs for achievements")
        if not has_action_verbs:
            analysis['recommendations'].append("Start each bullet point with strong action verbs")
        if not has_quantifiable:
            analysis['recommendations'].append("Add quantifiable results to {}% of your achievements".format(100 - int(analysis['quantifiable_impact_percentage'])))
        
        return analysis

    def analyze_education(self, text: str) -> Dict:
        """Analyze education section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Check for institution names
        institution_indicators = ['university', 'college', 'institute', 'school', 'academy']
        has_institution = any(indicator in text_lower for indicator in institution_indicators)
        analysis['checklist']['institution_name'] = has_institution
        
        # Check for degree names
        degree_patterns = [
            r'\b(bachelor|master|phd|doctorate|associate|diploma)\b',
            r'\b(b\.?[sa]\.?|m\.?[sa]\.?|ph\.?d\.?|m\.?b\.?a\.?)\b'
        ]
        has_degree = any(re.search(pattern, text_lower) for pattern in degree_patterns)
        analysis['checklist']['degree_name'] = has_degree
        
        # Check for graduation dates
        education_years = re.findall(r'\b(19|20)\d{2}\b', text)
        has_dates = len(education_years) > 0
        analysis['checklist']['graduation_dates'] = has_dates
        
        # Check for relevant coursework (more common for entry-level)
        coursework_indicators = ['coursework', 'relevant courses', 'courses', 'curriculum']
        has_coursework = any(indicator in text_lower for indicator in coursework_indicators)
        analysis['checklist']['relevant_coursework'] = has_coursework
        
        # Check for GPA (only if strong)
        gpa_pattern = r'gpa\s*:?\s*([3-4]\.[5-9]|4\.0)'
        has_strong_gpa = bool(re.search(gpa_pattern, text_lower))
        analysis['checklist']['gpa_included'] = has_strong_gpa or 'gpa' not in text_lower  # Good if no GPA or strong GPA
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_institution:
            analysis['recommendations'].append("Include full institution names")
        if not has_degree:
            analysis['recommendations'].append("Specify degree type (B.A., B.Sc., MBA, etc.)")
        if not has_dates:
            analysis['recommendations'].append("Add graduation dates or 'Expected' for current students")
        if not has_coursework and 'entry' in text_lower:
            analysis['recommendations'].append("Include relevant coursework for entry-level positions")
        
        return analysis

    def analyze_certifications(self, text: str, job_description: str = None) -> Dict:
        """Analyze certifications section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'certifications_found': [],
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Find certifications
        found_certs = []
        for cert in self.certifications:
            if cert in text_lower:
                found_certs.append(cert)
        
        analysis['certifications_found'] = found_certs
        
        # Check for industry-specific certifications
        has_industry_certs = len(found_certs) > 0
        analysis['checklist']['industry_certifications'] = has_industry_certs
        
        # Check if certifications are current (assume valid if mentioned)
        analysis['checklist']['valid_not_expired'] = True  # Hard to verify without dates
        
        # Check for acronym expansion
        cert_acronyms = ['pmp', 'cfa', 'cpa', 'cissp', 'aws', 'csm']
        has_expansions = any(f"{acronym}" in text_lower and len([word for word in text.split() if acronym.upper() in word.upper()]) > 1 
                           for acronym in cert_acronyms if acronym in text_lower)
        analysis['checklist']['acronyms_spelled_out'] = has_expansions or len(found_certs) == 0
        
        # Check for separate section
        cert_section_indicators = ['certification', 'license', 'credential']
        has_separate_section = any(indicator in text_lower for indicator in cert_section_indicators)
        analysis['checklist']['separate_section'] = has_separate_section or len(found_certs) == 0
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_industry_certs:
            if job_description:
                # Suggest relevant certifications based on job description
                jd_lower = job_description.lower()
                if 'project management' in jd_lower:
                    analysis['recommendations'].append("Consider adding PMP certification for project management roles")
                elif 'aws' in jd_lower or 'cloud' in jd_lower:
                    analysis['recommendations'].append("Add AWS certifications for cloud roles")
                elif 'google analytics' in jd_lower or 'marketing' in jd_lower:
                    analysis['recommendations'].append("Add Google Analytics certification for marketing roles")
                else:
                    analysis['recommendations'].append("Add relevant industry certifications")
            else:
                analysis['recommendations'].append("Include relevant professional certifications if available")
        
        if not has_separate_section and found_certs:
            analysis['recommendations'].append("Create a separate Certifications section")
        
        return analysis

    def analyze_projects_achievements(self, text: str) -> Dict:
        """Analyze projects and achievements section"""
        analysis = {
            'checklist': {},
            'score': 0,
            'measurable_percentage': 0,
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        # Check for projects section
        project_indicators = ['project', 'achievement', 'accomplishment', 'portfolio', 'volunteer']
        has_projects = any(indicator in text_lower for indicator in project_indicators)
        analysis['checklist']['projects_described'] = has_projects
        
        # Check for technology/skills used
        tech_mentioned = any(skill in text_lower for category in self.skill_categories['technical'].values() for skill in category)
        analysis['checklist']['technology_skills_listed'] = tech_mentioned
        
        # Check for measurable achievements
        measurable_patterns = [r'\b\d+%', r'\$\d+', r'\b\d+\s*(users|students|people|clients)', r'trained \d+', r'helped \d+']
        measurable_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in measurable_patterns)
        
        total_achievements = text_lower.count('project') + text_lower.count('achievement') + text_lower.count('volunteer')
        if total_achievements > 0:
            analysis['measurable_percentage'] = (measurable_count / total_achievements) * 100
        
        has_measurable = analysis['measurable_percentage'] > 30
        analysis['checklist']['measurable_achievements'] = has_measurable
        
        # Check for relevant volunteer work
        volunteer_keywords = ['volunteer', 'community', 'nonprofit', 'charity', 'leadership']
        has_relevant_volunteer = any(keyword in text_lower for keyword in volunteer_keywords)
        analysis['checklist']['relevant_volunteer'] = has_relevant_volunteer or not any('volunteer' in text_lower for _ in range(1))
        
        # Check for vague descriptions
        vague_words = ['helped', 'worked on', 'participated', 'involved', 'responsible for']
        vague_count = sum(text_lower.count(word) for word in vague_words)
        total_words = len(text.split())
        has_specific_descriptions = (vague_count / total_words * 100) < 5 if total_words > 0 else True
        analysis['checklist']['no_vague_descriptions'] = has_specific_descriptions
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if not has_projects:
            analysis['recommendations'].append("Add a Projects or Achievements section to showcase your work")
        if not tech_mentioned:
            analysis['recommendations'].append("Include technologies and skills used in your projects")
        if not has_measurable:
            analysis['recommendations'].append("Quantify project outcomes (e.g., 'trained 50 students', 'increased efficiency by 25%')")
        if not has_specific_descriptions:
            analysis['recommendations'].append("Replace vague descriptions with specific, action-oriented language")
        
        return analysis

    def analyze_keywords_relevance(self, text: str, job_description: str = None, job_title: str = None) -> Dict:
        """Analyze keywords and industry relevance"""
        analysis = {
            'checklist': {},
            'score': 0,
            'keyword_match_percentage': 0,
            'missing_keywords': [],
            'recommendations': []
        }
        
        text_lower = text.lower()
        
        if job_description:
            jd_lower = job_description.lower()
            
            # Extract keywords from job description
            jd_words = set(re.findall(r'\b\w{4,}\b', jd_lower))
            
            # Remove common words
            common_words = {'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their'}
            jd_keywords = jd_words - common_words
            
            # Find matching keywords
            resume_words = set(re.findall(r'\b\w{4,}\b', text_lower))
            matched_keywords = jd_keywords & resume_words
            
            # Calculate match percentage
            analysis['keyword_match_percentage'] = (len(matched_keywords) / len(jd_keywords)) * 100 if jd_keywords else 0
            
            # Find missing important keywords
            missing = list(jd_keywords - resume_words)[:10]  # Top 10 missing
            analysis['missing_keywords'] = missing
            
            analysis['checklist']['jd_keywords_included'] = analysis['keyword_match_percentage'] > 60
        else:
            analysis['checklist']['jd_keywords_included'] = True
        
        # Check hard and soft skills balance
        tech_skills = sum(1 for category in self.skill_categories['technical'].values() for skill in category if skill in text_lower)
        soft_skills = sum(1 for skill in self.skill_categories['soft'] if skill in text_lower)
        
        has_balance = tech_skills > 0 and soft_skills > 0
        analysis['checklist']['hard_soft_balance'] = has_balance
        
        # Check industry terms usage
        if job_title:
            industry = self.detect_industry_from_title(job_title)
            if industry:
                industry_terms = self.get_industry_terms(industry)
                industry_usage = sum(1 for term in industry_terms if term in text_lower)
                has_industry_terms = industry_usage > 2
            else:
                has_industry_terms = True
        else:
            has_industry_terms = True
        
        analysis['checklist']['industry_terms'] = has_industry_terms
        
        # Check keyword frequency (2-3 times per important keyword)
        important_keywords = ['experience', 'management', 'development', 'analysis', 'project']
        appropriate_frequency = all(2 <= text_lower.count(keyword) <= 5 for keyword in important_keywords if keyword in text_lower)
        analysis['checklist']['appropriate_frequency'] = appropriate_frequency
        
        # Check for keyword stuffing
        word_count = len(text.split())
        keyword_density = (tech_skills + soft_skills) / word_count * 100 if word_count > 0 else 0
        no_stuffing = keyword_density < 15
        analysis['checklist']['no_keyword_stuffing'] = no_stuffing
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        if job_description and analysis['keyword_match_percentage'] < 60:
            analysis['recommendations'].append(f"Add missing keywords: {', '.join(analysis['missing_keywords'][:5])}")
        if not has_balance:
            analysis['recommendations'].append("Include both technical and soft skills throughout your resume")
        if not has_industry_terms:
            analysis['recommendations'].append("Use more industry-specific terminology")
        if not no_stuffing:
            analysis['recommendations'].append("Reduce keyword density - use keywords naturally")
        
        return analysis

    def analyze_formatting_readability(self, text: str, formatting_info: Dict) -> Dict:
        """Analyze formatting and readability"""
        analysis = {
            'checklist': {},
            'score': 0,
            'recommendations': []
        }
        
        # File format (assumed good if parsed successfully)
        analysis['checklist']['ats_safe_format'] = True
        
        # Check for images/graphics
        has_no_images = not formatting_info.get('has_images', False)
        analysis['checklist']['no_images'] = has_no_images
        
        # Check for tables
        has_no_tables = not formatting_info.get('has_tables', False)
        analysis['checklist']['no_tables'] = has_no_tables
        
        # Check section headings
        standard_headings = ['experience', 'education', 'skills', 'summary']
        headings_found = sum(1 for heading in standard_headings if heading in text.lower())
        has_standard_headings = headings_found >= 3
        analysis['checklist']['standard_headings'] = has_standard_headings
        
        # Check fonts (if available)
        fonts_used = formatting_info.get('fonts_used', set())
        if fonts_used:
            ats_friendly_fonts = any(ats_font in font.lower() for font in fonts_used for ats_font in self.ats_fonts)
            analysis['checklist']['ats_friendly_fonts'] = ats_friendly_fonts
        else:
            analysis['checklist']['ats_friendly_fonts'] = True  # Assume good if no font info
        
        # Check font size (hard to determine from text, assume good)
        analysis['checklist']['appropriate_font_size'] = True
        
        # Check spacing and alignment (heuristic based on text structure)
        lines = text.split('\n')
        consistent_spacing = len([line for line in lines if line.strip()]) / len(lines) > 0.5
        analysis['checklist']['consistent_spacing'] = consistent_spacing
        
        # Check for bullet points
        bullet_patterns = [r'•', r'●', r'▪', r'-\s', r'\*\s']
        has_bullets = any(re.search(pattern, text) for pattern in bullet_patterns)
        analysis['checklist']['bullet_points_used'] = has_bullets
        
        # Check readability
        try:
            readability_score = textstat.flesch_reading_ease(text)
            good_readability = readability_score > 30  # Reasonable for professional content
        except:
            good_readability = True  # Default if analysis fails
        
        analysis['checklist']['good_readability'] = good_readability
        
        # Calculate score
        checklist_items = list(analysis['checklist'].values())
        analysis['score'] = (sum(checklist_items) / len(checklist_items)) * 100
        
        # Generate recommendations
        formatting_issues = formatting_info.get('formatting_issues', [])
        if formatting_issues:
            analysis['recommendations'].extend(formatting_issues)
        
        if not has_no_images:
            analysis['recommendations'].append("Remove images and graphics for better ATS compatibility")
        if not has_no_tables:
            analysis['recommendations'].append("Replace tables with simple text formatting")
        if not has_standard_headings:
            analysis['recommendations'].append("Use standard section headings (Work Experience, Education, Skills)")
        if not has_bullets:
            analysis['recommendations'].append("Use bullet points instead of paragraphs for better readability")
        
        return analysis

    def calculate_component_scores(self, contact, headline, skills, experience, education, certifications, projects, keywords, formatting) -> Dict:
        """Calculate weighted component scores"""
        
        # Weights based on ATS importance
        weights = {
            'keyword_match': 0.25,
            'skills_match': 0.20,
            'formatting_readability': 0.20,
            'experience_relevance': 0.15,
            'contact_completeness': 0.10,
            'education_certifications': 0.10
        }
        
        # Component scores
        scores = {
            'keyword_match': keywords['score'],
            'skills_match': skills['score'],
            'formatting_readability': formatting['score'],
            'experience_relevance': experience['score'],
            'contact_completeness': contact['score'],
            'education_certifications': (education['score'] + certifications['score']) / 2
        }
        
        # Calculate overall score
        overall_score = sum(scores[component] * weights[component] for component in scores)
        
        scores['overall_ats_score'] = int(overall_score)
        
        return scores

    def generate_executive_summary(self, scores: Dict, keywords_analysis: Dict) -> Dict:
        """Generate executive summary"""
        overall_score = scores['overall_ats_score']
        keyword_match = scores['keyword_match']
        skills_match = scores['skills_match']
        formatting_score = scores['formatting_readability']
        
        # Generate summary statement
        if overall_score >= 80:
            summary = "Excellent ATS optimization with strong keyword alignment and professional formatting. Minor improvements could further enhance visibility."
        elif overall_score >= 65:
            summary = "Good ATS compatibility with solid structure. Focus on keyword optimization and quantified achievements for better results."
        elif overall_score >= 50:
            summary = "Moderate ATS readiness requiring improvements in formatting, keywords, and content structure for optimal performance."
        else:
            summary = "Significant ATS optimization needed. Address formatting issues, add missing keywords, and improve overall structure."
        
        return {
            'overall_ats_score': overall_score,
            'keyword_match': int(keyword_match),
            'skills_match': int(skills_match),
            'formatting_readability': int(formatting_score),
            'summary_statement': summary
        }

    def prepare_pie_chart_data(self, scores: Dict) -> List[Dict]:
        """Prepare data for pie chart visualization"""
        return [
            {'name': 'Keyword Match', 'value': int(scores['keyword_match']), 'color': '#3B82F6'},
            {'name': 'Skills Match', 'value': int(scores['skills_match']), 'color': '#10B981'},
            {'name': 'Formatting', 'value': int(scores['formatting_readability']), 'color': '#F59E0B'},
            {'name': 'Experience', 'value': int(scores['experience_relevance']), 'color': '#EF4444'},
            {'name': 'Contact & Education', 'value': int(scores['education_certifications']), 'color': '#8B5CF6'}
        ]

    def generate_final_recommendations(self, contact, headline, skills, experience, education, certifications, formatting, keywords) -> List[str]:
        """Generate final 10-point recommendations"""
        all_recommendations = []
        
        # Collect all recommendations
        all_recommendations.extend(contact.get('recommendations', []))
        all_recommendations.extend(headline.get('recommendations', []))
        all_recommendations.extend(skills.get('recommendations', []))
        all_recommendations.extend(experience.get('recommendations', []))
        all_recommendations.extend(education.get('recommendations', []))
        all_recommendations.extend(certifications.get('recommendations', []))
        all_recommendations.extend(formatting.get('recommendations', []))
        all_recommendations.extend(keywords.get('recommendations', []))
        
        # Prioritize and limit to 10
        priority_recommendations = []
        
        # High priority items
        high_priority = [rec for rec in all_recommendations if any(word in rec.lower() for word in ['missing', 'add', 'include', 'critical'])]
        priority_recommendations.extend(high_priority[:4])
        
        # Medium priority items
        medium_priority = [rec for rec in all_recommendations if rec not in priority_recommendations and any(word in rec.lower() for word in ['improve', 'enhance', 'optimize'])]
        priority_recommendations.extend(medium_priority[:3])
        
        # Fill remaining slots
        remaining = [rec for rec in all_recommendations if rec not in priority_recommendations]
        priority_recommendations.extend(remaining[:3])
        
        # Ensure exactly 10 recommendations
        if len(priority_recommendations) < 10:
            generic_recommendations = [
                "Use consistent formatting throughout the resume",
                "Proofread for grammar and spelling errors",
                "Tailor resume content to specific job applications"
            ]
            priority_recommendations.extend(generic_recommendations[:10-len(priority_recommendations)])
        
        return priority_recommendations[:10]

    def detect_industry_from_title(self, job_title: str) -> str:
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
        
        return 'general'

    def get_industry_terms(self, industry: str) -> List[str]:
        """Get industry-specific terms"""
        industry_terms = {
            'technology': ['software', 'development', 'programming', 'coding', 'algorithm', 'database', 'api'],
            'marketing': ['campaign', 'branding', 'social media', 'content', 'analytics', 'seo', 'conversion'],
            'finance': ['financial', 'analysis', 'modeling', 'risk', 'compliance', 'reporting', 'budgeting'],
            'healthcare': ['patient', 'clinical', 'medical', 'treatment', 'diagnosis', 'therapy', 'care'],
            'sales': ['sales', 'revenue', 'client', 'customer', 'relationship', 'negotiation', 'pipeline']
        }
        
        return industry_terms.get(industry, [])
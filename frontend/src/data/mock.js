// Mock data for ATS Resume Checker

export const mockAnalysisResult = {
  overallScore: 78,
  atsCompatibility: 85,
  keywordMatch: 72,
  skillsMatch: 80,
  formatScore: 90,
  
  issues: [
    {
      type: 'critical',
      category: 'Keywords',
      title: 'Missing important keywords',
      description: 'Your resume is missing 5 important keywords from the job description',
      suggestions: ['Add "project management" to your experience section', 'Include "agile methodology" in skills', 'Mention "stakeholder communication"']
    },
    {
      type: 'warning',
      category: 'Formatting',
      title: 'Complex formatting detected',
      description: 'Some formatting elements may not be ATS-friendly',
      suggestions: ['Remove tables and use bullet points', 'Avoid text boxes and graphics', 'Use standard fonts like Arial or Calibri']
    },
    {
      type: 'info',
      category: 'Skills',
      title: 'Skills section optimization',
      description: 'Your skills section could be improved for better ATS parsing',
      suggestions: ['Group similar skills together', 'Use industry-standard skill names', 'Add skill proficiency levels']
    }
  ],

  missingKeywords: [
    { keyword: 'project management', importance: 'high', frequency: 8 },
    { keyword: 'agile methodology', importance: 'high', frequency: 6 },
    { keyword: 'stakeholder communication', importance: 'medium', frequency: 4 },
    { keyword: 'data analysis', importance: 'medium', frequency: 5 },
    { keyword: 'cross-functional teams', importance: 'low', frequency: 3 }
  ],

  foundKeywords: [
    { keyword: 'javascript', importance: 'high', frequency: 12, present: true },
    { keyword: 'react', importance: 'high', frequency: 10, present: true },
    { keyword: 'node.js', importance: 'medium', frequency: 7, present: true },
    { keyword: 'mongodb', importance: 'medium', frequency: 5, present: true },
    { keyword: 'api development', importance: 'high', frequency: 9, present: true }
  ],

  sections: {
    contact: { present: true, score: 95, issues: [] },
    summary: { present: true, score: 80, issues: ['Consider adding more specific achievements'] },
    experience: { present: true, score: 75, issues: ['Add more quantified results', 'Include missing keywords'] },
    education: { present: true, score: 90, issues: [] },
    skills: { present: true, score: 70, issues: ['Reorganize skills by category', 'Add technical proficiency levels'] },
    certifications: { present: false, score: 0, issues: ['Consider adding relevant certifications'] }
  },

  recommendations: [
    {
      priority: 'high',
      title: 'Add Missing Keywords',
      description: 'Include the top 5 missing keywords in relevant sections of your resume',
      impact: '+15 points'
    },
    {
      priority: 'high',
      title: 'Quantify Achievements',
      description: 'Add specific numbers and percentages to your accomplishments',
      impact: '+10 points'
    },
    {
      priority: 'medium',
      title: 'Optimize Skills Section',
      description: 'Reorganize skills with proficiency levels and group by category',
      impact: '+8 points'
    },
    {
      priority: 'low',
      title: 'Add Certifications',
      description: 'Include relevant professional certifications if available',
      impact: '+5 points'
    }
  ]
};

export const mockJobDescription = `We are seeking a talented Software Engineer to join our dynamic team. The ideal candidate will have experience in full-stack development, project management, and agile methodology.

Key Responsibilities:
- Develop and maintain web applications using JavaScript, React, and Node.js
- Collaborate with cross-functional teams to deliver high-quality software solutions
- Participate in agile development processes and sprint planning
- Conduct data analysis to inform product decisions
- Manage stakeholder communication and project timelines
- Write clean, maintainable code following best practices

Required Skills:
- 3+ years of experience in JavaScript and React development
- Strong knowledge of Node.js and MongoDB
- Experience with API development and integration
- Project management skills and experience with agile methodology
- Excellent stakeholder communication abilities
- Data analysis and problem-solving skills
- Experience working with cross-functional teams

Preferred Qualifications:
- Bachelor's degree in Computer Science or related field
- AWS or cloud platform experience
- Experience with testing frameworks
- Knowledge of CI/CD pipelines`;

export const industryTips = [
  {
    industry: 'Technology',
    tips: [
      'Include specific programming languages and frameworks',
      'Mention version control systems like Git',
      'Highlight open-source contributions',
      'Add links to your GitHub profile or portfolio'
    ]
  },
  {
    industry: 'Finance',
    tips: [
      'Emphasize analytical and quantitative skills',
      'Include relevant certifications (CFA, FRM, etc.)',
      'Mention financial modeling experience',
      'Highlight regulatory compliance knowledge'
    ]
  },
  {
    industry: 'Healthcare',
    tips: [
      'Include relevant medical certifications',
      'Emphasize patient care experience',
      'Mention EMR/EHR system experience',
      'Highlight compliance with healthcare regulations'
    ]
  }
];

export const atsSettings = {
  keywordDensity: {
    minimum: 2,
    maximum: 8,
    optimal: 4
  },
  sectionWeights: {
    contact: 10,
    summary: 15,
    experience: 40,
    education: 15,
    skills: 15,
    certifications: 5
  },
  formatRules: [
    'Use standard fonts (Arial, Calibri, Times New Roman)',
    'Avoid tables, text boxes, and graphics',
    'Use bullet points instead of paragraphs',
    'Include section headers in standard format',
    'Maintain consistent formatting throughout'
  ]
};
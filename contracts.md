# ATS Resume Checker - API Contracts & Integration Plan

## Overview
This document outlines the API contracts, mocked data replacement strategy, and implementation plan for the ATS Resume Checker full-stack application.

## Frontend Mock Data to Replace
Currently using mock data from `/frontend/src/data/mock.js`:
- `mockAnalysisResult` - Complete analysis results including scores, issues, and recommendations
- `mockJobDescription` - Sample job description for testing
- File upload simulation

## API Endpoints

### 1. Resume Upload & Analysis
```
POST /api/resume/analyze
Content-Type: multipart/form-data
Body: {
  file: [resume file - PDF/DOC/DOCX],
  jobDescription?: string (optional)
}
Response: {
  success: boolean,
  data: {
    analysisId: string,
    overallScore: number,
    atsCompatibility: number,
    keywordMatch: number,
    skillsMatch: number,
    formatScore: number,
    issues: Issue[],
    missingKeywords: Keyword[],
    foundKeywords: Keyword[],
    sections: SectionAnalysis,
    recommendations: Recommendation[]
  }
}
```

### 2. Keyword Analysis
```
POST /api/resume/keywords
Body: {
  resumeText: string,
  jobDescription: string
}
Response: {
  success: boolean,
  data: {
    missingKeywords: Keyword[],
    foundKeywords: Keyword[],
    keywordMatch: number
  }
}
```

### 3. Get Analysis History
```
GET /api/resume/history
Response: {
  success: boolean,
  data: Analysis[]
}
```

## Data Models

### Analysis Result
```typescript
interface Analysis {
  id: string;
  fileName: string;
  uploadDate: Date;
  overallScore: number;
  atsCompatibility: number;
  keywordMatch: number;
  skillsMatch: number;
  formatScore: number;
  issues: Issue[];
  missingKeywords: Keyword[];
  foundKeywords: Keyword[];
  sections: SectionAnalysis;
  recommendations: Recommendation[];
}
```

### Issue
```typescript
interface Issue {
  type: 'critical' | 'warning' | 'info';
  category: string;
  title: string;
  description: string;
  suggestions: string[];
}
```

### Keyword
```typescript
interface Keyword {
  keyword: string;
  importance: 'high' | 'medium' | 'low';
  frequency: number;
  present?: boolean;
}
```

## Backend Implementation Requirements

### 1. Resume Parsing Engine
- **PDF Parsing**: Use PyMuPDF (fitz) or pdfplumber for PDF text extraction
- **DOC/DOCX Parsing**: Use python-docx for Word document parsing
- **Text Cleaning**: Remove formatting artifacts, normalize whitespace
- **Section Detection**: Identify resume sections (contact, summary, experience, etc.)

### 2. ATS Analysis Engine
- **Format Analysis**: Check for ATS-friendly formatting
- **Keyword Extraction**: NLP-based keyword extraction and matching
- **Skills Detection**: Match skills against job requirements
- **Section Validation**: Ensure all required sections are present
- **Scoring Algorithm**: Calculate weighted scores for each component

### 3. Keyword Matching System
- **Job Description Parsing**: Extract requirements and keywords from JD
- **Semantic Matching**: Use word similarity for better matching
- **Frequency Analysis**: Count keyword occurrences
- **Importance Ranking**: Rank keywords by importance in JD

### 4. File Storage
- **Resume Storage**: Store uploaded files securely
- **Analysis Caching**: Cache analysis results for re-analysis
- **Temporary Files**: Clean up uploaded files after processing

## Database Schema

### analyses Collection
```javascript
{
  _id: ObjectId,
  fileName: String,
  fileSize: Number,
  uploadDate: Date,
  originalText: String,
  jobDescription: String,
  scores: {
    overall: Number,
    atsCompatibility: Number,
    keywordMatch: Number,
    skillsMatch: Number,
    formatScore: Number
  },
  analysis: {
    issues: Array,
    missingKeywords: Array,
    foundKeywords: Array,
    sections: Object,
    recommendations: Array
  },
  metadata: {
    fileType: String,
    processingTime: Number,
    version: String
  }
}
```

## Frontend Integration Changes

### 1. Remove Mock Data
- Remove hardcoded `mockAnalysisResult` usage
- Replace with actual API calls

### 2. API Integration Points
- `UploadSection.jsx`: Replace mock upload with actual file upload
- `App.js`: Replace setTimeout with actual API calls
- `JobDescriptionInput.jsx`: Integrate with keyword re-analysis

### 3. Error Handling
- Add proper error states for failed uploads
- Handle parsing errors gracefully
- Show progress indicators during processing

### 4. Real-time Updates
- WebSocket integration for analysis progress
- Live scoring updates as analysis progresses

## Required Dependencies

### Backend
```
PyMuPDF==1.23.14          # PDF parsing
python-docx==1.1.0        # Word document parsing
nltk==3.8.1               # Natural language processing
scikit-learn==1.3.2       # ML for text analysis
spacy==3.7.2              # Advanced NLP
python-multipart==0.0.6   # File upload handling
aiofiles==23.2.1          # Async file operations
```

### NLP Models
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords wordnet
```

## Testing Strategy
1. **Unit Tests**: Test individual parsing and analysis functions
2. **Integration Tests**: Test complete analysis pipeline
3. **File Format Tests**: Test various resume formats and structures
4. **Performance Tests**: Ensure sub-10 second analysis time
5. **Accuracy Tests**: Validate analysis quality with sample resumes

## Deployment Considerations
- File upload size limits (10MB max)
- Processing timeout limits (30 seconds max)
- Concurrent analysis limits
- File cleanup and storage management
- Security scanning for uploaded files

## Success Metrics
- Analysis accuracy > 85%
- Processing time < 10 seconds
- File format support: PDF, DOC, DOCX
- Mobile responsiveness
- Error rate < 5%
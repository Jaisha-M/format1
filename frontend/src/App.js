import React, { useState } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import JobDescriptionInput from './components/JobDescriptionInput';
import ScoreDisplay from './components/ScoreDisplay';
import IssuesPanel from './components/IssuesPanel';
import SectionsAnalysis from './components/SectionsAnalysis';
import { Toaster } from './components/ui/toaster';
import { useToast } from './hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const { toast } = useToast();

  const handleFileUpload = async (file) => {
    setUploadedFile(file);
    setUploadStatus('uploading');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (jobDescription) {
        formData.append('job_description', jobDescription);
      }

      const response = await axios.post(`${API}/resume/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout
      });

      if (response.data.success) {
        setAnalysisResult(response.data.data);
        setUploadStatus('success');
        toast({
          title: "Analysis Complete!",
          description: `Your resume scored ${response.data.data.overall_score}% overall.`
        });
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
      
      let errorMessage = 'Failed to analyze resume. Please try again.';
      if (error.response?.status === 400) {
        errorMessage = error.response.data.detail || 'Invalid file format or size.';
      } else if (error.response?.status === 422) {
        errorMessage = 'Could not parse resume content. Please ensure it\'s a text-based document.';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Analysis timeout. Please try with a smaller file.';
      }
      
      toast({
        title: "Analysis Failed",
        description: errorMessage,
        variant: "destructive"
      });
    }
  };

  const handleJobDescriptionChange = async (description) => {
    setJobDescription(description);
    
    // If we already have analysis results and a new job description is provided,
    // re-analyze for keyword matching
    if (analysisResult && description && uploadedFile) {
      try {
        const response = await axios.post(`${API}/resume/keywords`, {
          resume_text: analysisResult.raw_text || '',
          job_description: description
        });

        if (response.data.success) {
          // Update the analysis result with new keyword data
          setAnalysisResult(prev => ({
            ...prev,
            keyword_match: response.data.data.keyword_match,
            missing_keywords: response.data.data.missing_keywords,
            found_keywords: response.data.data.found_keywords,
            // Recalculate overall score
            overall_score: Math.round((
              prev.ats_compatibility * 0.25 +
              prev.format_score * 0.25 +
              response.data.data.keyword_match * 0.30 +
              prev.skills_match * 0.20
            ))
          }));
          
          toast({
            title: "Keywords Updated",
            description: `Updated keyword matching based on job description.`
          });
        }
      } catch (error) {
        console.error('Keyword analysis error:', error);
        toast({
          title: "Keyword Analysis Failed",
          description: "Could not analyze keywords with job description.",
          variant: "destructive"
        });
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI-Powered ATS Resume Checker
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Optimize your resume for Applicant Tracking Systems and increase your chances of landing interviews.
            Get instant feedback and actionable suggestions.
          </p>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <UploadSection 
            onFileUpload={handleFileUpload}
            uploadStatus={uploadStatus}
          />
          
          {/* Demo Button */}
          {!analysisResult && (
            <div className="text-center mt-4">
              <Button 
                variant="outline" 
                onClick={async () => {
                  // Create a demo file for analysis
                  const demoResumeText = `John Doe
Software Engineer
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5 years of experience in full-stack development using JavaScript, React, and Node.js.

EXPERIENCE
Senior Software Developer | Tech Company | 2020-2024
• Developed web applications using React and Node.js
• Collaborated with cross-functional teams on agile projects
• Implemented API development and database management

EDUCATION
Bachelor of Science in Computer Science | University | 2019

SKILLS
JavaScript, React, Node.js, MongoDB, Git, Agile, Team Leadership`;
                  
                  // Create a blob and file for demo
                  const blob = new Blob([demoResumeText], { type: 'text/plain' });
                  const demoFile = new File([blob], 'demo-resume.txt', { type: 'text/plain' });
                  
                  // Trigger analysis with demo file
                  await handleFileUpload(demoFile);
                }}
                className="text-blue-600 border-blue-600 hover:bg-blue-50"
                disabled={uploadStatus === 'uploading'}
              >
                🚀 Try Demo Analysis
              </Button>
              <p className="text-xs text-gray-500 mt-2">
                See how our ATS checker works with sample data
              </p>
            </div>
          )}
        </div>

        {/* Job Description Input */}
        {(uploadedFile || analysisResult) && (
          <div className="mb-8">
            <JobDescriptionInput
              onJobDescriptionChange={handleJobDescriptionChange}
              jobDescription={jobDescription}
            />
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-8">
            {/* Score Display */}
            <ScoreDisplay analysisResult={analysisResult} />

            {/* Two Column Layout for Issues and Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <IssuesPanel analysisResult={analysisResult} />
              </div>
              <div className="lg:col-span-1">
                <SectionsAnalysis sections={analysisResult.sections} />
              </div>
            </div>
          </div>
        )}

        {/* Features Section (when no file uploaded) */}
        {!uploadedFile && !analysisResult && (
          <div className="mt-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Why Use Our ATS Resume Checker?
              </h2>
              <p className="text-lg text-gray-600">
                Get professional insights to optimize your resume for modern hiring systems
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6">
                <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🎯</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Keyword Optimization</h3>
                <p className="text-gray-600">
                  Match your resume keywords with job requirements to pass ATS filtering
                </p>
              </div>

              <div className="text-center p-6">
                <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">ATS Compatibility</h3>
                <p className="text-gray-600">
                  Ensure your resume format is readable by all major ATS systems
                </p>
              </div>

              <div className="text-center p-6">
                <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">⚡</span>
                </div>
                <h3 className="text-xl font-semibold mb-2">Instant Feedback</h3>
                <p className="text-gray-600">
                  Get immediate suggestions and improvements for your resume
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
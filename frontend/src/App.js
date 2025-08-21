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
import { mockAnalysisResult } from './data/mock';

const HomePage = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  const handleFileUpload = (file) => {
    setUploadedFile(file);
    setUploadStatus('uploading');
    
    // Simulate analysis with mock data
    setTimeout(() => {
      setAnalysisResult(mockAnalysisResult);
      setUploadStatus('success');
    }, 2000);
  };

  const handleJobDescriptionChange = (description) => {
    setJobDescription(description);
    // In real implementation, this would re-analyze the resume with new job description
    if (analysisResult && description) {
      // Update analysis result with new keyword matching
      console.log('Re-analyzing with job description:', description);
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
                onClick={() => {
                  setAnalysisResult(mockAnalysisResult);
                  setUploadStatus('success');
                  setUploadedFile(new File([''], 'demo-resume.pdf'));
                }}
                className="text-blue-600 border-blue-600 hover:bg-blue-50"
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
import React, { useState } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [file, setFile] = useState(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a resume file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (jobTitle.trim()) {
        formData.append('job_title', jobTitle.trim());
      }
      if (jobDescription.trim()) {
        formData.append('job_description', jobDescription.trim());
      }

      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Analysis failed');
      }
    } catch (err) {
      setError('Upload failed. Please try again.');
    }

    setLoading(false);
  };

  const resetForm = () => {
    setFile(null);
    setJobTitle('');
    setJobDescription('');
    setResults(null);
    setError('');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBarColor = (score) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Bruwrite ATS Resume Checker
          </h1>
          <p className="text-lg text-gray-600">
            Optimize your resume for Applicant Tracking Systems and increase your interview chances
          </p>
        </div>

        {!results ? (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Resume Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Resume * (PDF, DOC, DOCX, TXT)
                </label>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border-2 border-dashed border-gray-300 rounded-lg p-4"
                  required
                />
              </div>

              {/* Job Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title (Optional)
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g., Software Engineer, Marketing Manager"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Job Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description (Optional)
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here to get more accurate keyword matching and recommendations..."
                  rows="6"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Adding a job description will provide more accurate keyword analysis and tailored recommendations
                </p>
              </div>

              {error && (
                <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !file}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
              >
                {loading ? 'Analyzing Resume...' : 'Analyze Resume'}
              </button>
            </form>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Executive Summary */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Executive Summary</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className={`text-3xl font-bold mb-2 ${results.overall_score >= 80 ? 'text-green-600' : results.overall_score >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {results.overall_score}%
                  </div>
                  <div className="text-sm text-gray-600">Overall ATS Score</div>
                </div>
                <div className="text-center">
                  <div className={`text-3xl font-bold mb-2 ${results.keyword_match >= 80 ? 'text-green-600' : results.keyword_match >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {results.keyword_match}%
                  </div>
                  <div className="text-sm text-gray-600">Keyword Match</div>
                </div>
                <div className="text-center">
                  <div className={`text-3xl font-bold mb-2 ${results.skills_match >= 80 ? 'text-green-600' : results.skills_match >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {results.skills_match}%
                  </div>
                  <div className="text-sm text-gray-600">Skills Match</div>
                </div>
                <div className="text-center">
                  <div className={`text-3xl font-bold mb-2 ${results.formatting_readability >= 80 ? 'text-green-600' : results.formatting_readability >= 60 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {results.formatting_readability}%
                  </div>
                  <div className="text-sm text-gray-600">Formatting & Readability</div>
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">Summary Statement</h3>
                <p className="text-blue-800">{results.summary_statement}</p>
              </div>
            </div>

            {/* Detailed Section Analysis */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🔍 Detailed Section Analysis</h2>
              
              {/* Contact Information */}
              <div className="mb-6 border-b pb-4">
                <h3 className="text-lg font-semibold mb-3">A) Contact Information</h3>
                <div className="bg-gray-50 p-4 rounded">
                  <h4 className="font-medium mb-2">✅ Checklist Analysis:</h4>
                  {results.comprehensive_analysis?.detailed_analysis?.contact_information && (
                    <div className="space-y-1 text-sm">
                      {Object.entries(results.comprehensive_analysis.detailed_analysis.contact_information.checklist).map(([key, value]) => (
                        <div key={key} className="flex items-center">
                          <span className={value ? "text-green-600" : "text-red-600"}>
                            {value ? "✓" : "✗"}
                          </span>
                          <span className="ml-2">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <div className="mt-3">
                    <h4 className="font-medium mb-2">📌 Recommendations:</h4>
                    {results.comprehensive_analysis?.detailed_analysis?.contact_information?.recommendations?.map((rec, idx) => (
                      <div key={idx} className="text-sm text-gray-700">• {rec}</div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Skills Section Analysis */}
              <div className="mb-6 border-b pb-4">
                <h3 className="text-lg font-semibold mb-3">C) Skills Section</h3>
                <div className="bg-gray-50 p-4 rounded">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Technical Skills Found:</h4>
                      <div className="flex flex-wrap gap-1">
                        {results.comprehensive_analysis?.detailed_analysis?.skills_section?.skills_found?.technical?.map((skill, idx) => (
                          <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">{skill}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Soft Skills Found:</h4>
                      <div className="flex flex-wrap gap-1">
                        {results.comprehensive_analysis?.detailed_analysis?.skills_section?.skills_found?.soft?.map((skill, idx) => (
                          <span key={idx} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">{skill}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {results.comprehensive_analysis?.detailed_analysis?.skills_section?.job_match_percentage !== undefined && (
                    <div className="mt-3">
                      <div className="text-sm font-medium">
                        Job Description Match: {results.comprehensive_analysis.detailed_analysis.skills_section.job_match_percentage.toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Work Experience Analysis */}
              <div className="mb-6 border-b pb-4">
                <h3 className="text-lg font-semibold mb-3">D) Work Experience</h3>
                <div className="bg-gray-50 p-4 rounded">
                  {results.comprehensive_analysis?.detailed_analysis?.work_experience && (
                    <div>
                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div className="text-sm">
                          <span className="font-medium">Quantifiable Impact: </span>
                          <span className={results.comprehensive_analysis.detailed_analysis.work_experience.quantifiable_impact_percentage > 30 ? "text-green-600" : "text-red-600"}>
                            {results.comprehensive_analysis.detailed_analysis.work_experience.quantifiable_impact_percentage.toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-sm">
                          <span className="font-medium">Score: </span>
                          <span className={results.comprehensive_analysis.detailed_analysis.work_experience.score >= 70 ? "text-green-600" : "text-yellow-600"}>
                            {results.comprehensive_analysis.detailed_analysis.work_experience.score}%
                          </span>
                        </div>
                      </div>
                      
                      <h4 className="font-medium mb-2">📌 Recommendations:</h4>
                      {results.comprehensive_analysis.detailed_analysis.work_experience.recommendations?.map((rec, idx) => (
                        <div key={idx} className="text-sm text-gray-700">• {rec}</div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Keywords & Industry Relevance */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">H) Keywords & Industry Relevance</h3>
                <div className="bg-gray-50 p-4 rounded">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Keyword Match Analysis:</h4>
                      <div className="text-sm space-y-1">
                        <div>Match Percentage: <span className="font-medium">{results.keyword_match}%</span></div>
                        <div>Total Keywords Found: <span className="font-medium">{results.total_keywords}</span></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Missing Keywords:</h4>
                      <div className="flex flex-wrap gap-1">
                        {results.missing_keywords?.slice(0, 10).map((keyword, idx) => (
                          <span key={idx} className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Overall ATS Scorecard */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📈 Overall ATS Scorecard</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="space-y-4">
                    {[
                      { label: 'Keyword Match', score: results.keyword_match, color: 'blue' },
                      { label: 'Skills Match', score: results.skills_match, color: 'green' },
                      { label: 'Formatting & Structure', score: results.formatting_readability, color: 'yellow' },
                      { label: 'Experience Relevance', score: results.experience_score, color: 'purple' }
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="font-medium">{item.label}:</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-32 bg-gray-200 rounded-full h-3">
                            <div 
                              className={`h-3 rounded-full bg-${item.color}-600`}
                              style={{ width: `${item.score}%` }}
                            ></div>
                          </div>
                          <span className="font-bold w-12">{item.score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold mb-3">Overall ATS Readiness</h3>
                  <div className="text-center">
                    <div className={`text-6xl font-bold mb-2 ${getScoreColor(results.overall_score)}`}>
                      {results.overall_score}%
                    </div>
                    <div className="text-lg text-gray-600">
                      {results.overall_score >= 80 ? '🎉 Excellent' : 
                       results.overall_score >= 65 ? '👍 Good' : 
                       results.overall_score >= 50 ? '⚠️ Needs Work' : '❌ Poor'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Final Recommendations */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🎯 Final Recommendations - Top 10 Improvements</h2>
              
              <div className="space-y-3">
                {results.recommendations?.slice(0, 10).map((rec, idx) => (
                  <div key={idx} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <div className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">
                      {idx + 1}
                    </div>
                    <div className="text-gray-800">{rec}</div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">💡 Pro Tips for ATS Success:</h3>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>• Save your resume as both .docx and .pdf versions</li>
                  <li>• Use standard section headings (Work Experience, Education, Skills)</li>
                  <li>• Include keywords naturally throughout your resume, not just in a skills section</li>
                  <li>• Quantify your achievements with specific numbers and percentages</li>
                  <li>• Keep formatting simple - avoid tables, text boxes, and complex layouts</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
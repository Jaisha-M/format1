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
            {/* Header with Reset Button */}
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <button
                onClick={resetForm}
                className="bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Check Another Resume
              </button>
            </div>

            {/* Overall Score */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Overall ATS Compatibility Score
                </h3>
                <div className={`text-5xl font-bold mb-4 ${getScoreColor(results.overall_score)}`}>
                  {results.overall_score}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-6 mb-4">
                  <div 
                    className={`h-6 rounded-full transition-all duration-500 ${getScoreBarColor(results.overall_score)}`}
                    style={{ width: `${results.overall_score}%` }}
                  ></div>
                </div>
                <p className="text-gray-600">
                  {results.overall_score >= 80 
                    ? '✅ Excellent! Your resume is well-optimized for ATS systems.'
                    : results.overall_score >= 60
                    ? '⚠️ Good progress! Some improvements could boost your score.'
                    : '❌ Your resume needs significant optimization for ATS compatibility.'
                  }
                </p>
              </div>
            </div>

            {/* Detailed Scores Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Format & Structure', score: results.format_score, icon: '📄' },
                { label: 'Keyword Match', score: results.keyword_score, icon: '🔍' },
                { label: 'Skills Alignment', score: results.skills_score, icon: '🎯' },
                { label: 'Experience Relevance', score: results.experience_score, icon: '💼' }
              ].map((item, index) => (
                <div key={index} className="bg-white rounded-lg shadow p-6 text-center">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <h4 className="font-semibold text-gray-700 mb-2">{item.label}</h4>
                  <div className={`text-2xl font-bold mb-2 ${getScoreColor(item.score)}`}>
                    {item.score}%
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getScoreBarColor(item.score)}`}
                      style={{ width: `${item.score}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{results.total_keywords}</div>
                <div className="text-sm text-gray-600">Keywords Found</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{results.sections_count}/6</div>
                <div className="text-sm text-gray-600">Resume Sections</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{results.word_count}</div>
                <div className="text-sm text-gray-600">Total Words</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">{results.readability_score}%</div>
                <div className="text-sm text-gray-600">Readability</div>
              </div>
            </div>

            {/* Issues and Recommendations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Critical Issues */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold text-red-600 mb-4 flex items-center">
                  🚨 Critical Issues ({results.issues.filter(i => i.severity === 'critical').length})
                </h3>
                <div className="space-y-3">
                  {results.issues.filter(i => i.severity === 'critical').map((issue, index) => (
                    <div key={index} className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                      <h4 className="font-semibold text-red-800">{issue.title}</h4>
                      <p className="text-sm text-red-700 mt-1">{issue.description}</p>
                    </div>
                  ))}
                  {results.issues.filter(i => i.severity === 'warning').map((issue, index) => (
                    <div key={index} className="p-3 bg-yellow-50 border-l-4 border-yellow-500 rounded">
                      <h4 className="font-semibold text-yellow-800">{issue.title}</h4>
                      <p className="text-sm text-yellow-700 mt-1">{issue.description}</p>
                    </div>
                  ))}
                  {results.issues.length === 0 && (
                    <p className="text-gray-500 text-center py-4">✅ No major issues detected!</p>
                  )}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold text-green-600 mb-4 flex items-center">
                  💡 Recommendations ({results.recommendations.length})
                </h3>
                <div className="space-y-3">
                  {results.recommendations.map((rec, index) => (
                    <div key={index} className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="font-semibold text-green-800">{rec.title}</h4>
                        <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                          +{rec.impact} pts
                        </span>
                      </div>
                      <p className="text-sm text-green-700">{rec.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Missing Keywords (if job description provided) */}
            {results.missing_keywords && results.missing_keywords.length > 0 && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-bold text-blue-600 mb-4">
                  🔍 Missing Keywords from Job Description
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                  {results.missing_keywords.map((keyword, index) => (
                    <div key={index} className="bg-blue-100 text-blue-800 px-3 py-2 rounded-full text-sm text-center">
                      {keyword}
                    </div>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-4">
                  💡 Consider adding these keywords naturally throughout your resume to improve job relevance.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
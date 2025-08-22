import React, { useState } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [file, setFile] = useState(null);
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
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Analysis failed');
      }
    } catch (err) {
      setError('Upload failed. Please try again.');
    }

    setLoading(false);
  };

  const resetForm = () => {
    setFile(null);
    setResults(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            ATS Resume Checker
          </h1>
          <p className="text-lg text-gray-600">
            Upload your resume to check ATS compatibility and get improvement suggestions
          </p>
        </div>

        {!results ? (
          <div className="bg-white rounded-lg shadow p-6">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Resume (PDF, DOC, DOCX, TXT)
                </label>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !file}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Analyzing...' : 'Analyze Resume'}
              </button>
            </form>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Overall Score */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  ATS Compatibility Score
                </h2>
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {results.overall_score}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div 
                    className="bg-blue-600 h-4 rounded-full"
                    style={{ width: `${results.overall_score}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Detailed Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <h3 className="font-semibold text-gray-700">Format Score</h3>
                <div className="text-2xl font-bold text-green-600">{results.format_score}%</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <h3 className="font-semibold text-gray-700">Keywords Found</h3>
                <div className="text-2xl font-bold text-blue-600">{results.keywords_found}</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <h3 className="font-semibold text-gray-700">Sections Found</h3>
                <div className="text-2xl font-bold text-purple-600">{results.sections_found}</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <h3 className="font-semibold text-gray-700">Word Count</h3>
                <div className="text-2xl font-bold text-orange-600">{results.word_count}</div>
              </div>
            </div>

            {/* Issues & Recommendations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-red-600 mb-4">Issues Found</h3>
                {results.issues.length > 0 ? (
                  <ul className="space-y-2">
                    {results.issues.map((issue, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        {issue}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No major issues found!</p>
                )}
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-bold text-green-600 mb-4">Recommendations</h3>
                <ul className="space-y-2">
                  {results.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Reset Button */}
            <div className="text-center">
              <button
                onClick={resetForm}
                className="bg-gray-600 text-white py-2 px-6 rounded-lg hover:bg-gray-700"
              >
                Check Another Resume
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
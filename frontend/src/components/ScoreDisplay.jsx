import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { CheckCircle2, AlertTriangle, XCircle, TrendingUp } from 'lucide-react';

const ScoreDisplay = ({ analysisResult }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  const getScoreIcon = (score) => {
    if (score >= 80) return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const scoreCards = [
    {
      title: 'ATS Compatibility',
      score: analysisResult.atsCompatibility,
      description: 'How well your resume passes ATS systems'
    },
    {
      title: 'Keyword Match',
      score: analysisResult.keywordMatch,
      description: 'Alignment with job requirements'
    },
    {
      title: 'Skills Match',
      score: analysisResult.skillsMatch,
      description: 'Relevance of your skills'
    },
    {
      title: 'Format Score',
      score: analysisResult.formatScore,
      description: 'Resume structure and formatting'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center justify-between">
            <span className="text-xl font-bold text-gray-900">Overall ATS Score</span>
            <TrendingUp className="h-6 w-6 text-blue-600" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-3xl font-bold ${getScoreColor(analysisResult.overallScore)}`}>
                  {analysisResult.overallScore}%
                </span>
                {getScoreIcon(analysisResult.overallScore)}
              </div>
              <Progress 
                value={analysisResult.overallScore} 
                className="h-3"
              />
              <p className="text-sm text-gray-600 mt-2">
                {analysisResult.overallScore >= 80 
                  ? 'Excellent! Your resume is well-optimized for ATS systems.'
                  : analysisResult.overallScore >= 60
                  ? 'Good progress! A few improvements could boost your score.'
                  : 'Your resume needs optimization for better ATS performance.'
                }
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scoreCards.map((card, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-700">
                {card.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <span className={`text-2xl font-bold ${getScoreColor(card.score)}`}>
                  {card.score}%
                </span>
                {getScoreIcon(card.score)}
              </div>
              <Progress value={card.score} className="h-2 mb-2" />
              <p className="text-xs text-gray-500">{card.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ScoreDisplay;
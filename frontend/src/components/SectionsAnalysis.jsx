import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { CheckCircle2, XCircle, AlertTriangle, User, Briefcase, GraduationCap, Award, FileText, Target } from 'lucide-react';

const SectionsAnalysis = ({ sections }) => {
  const getSectionIcon = (sectionName) => {
    switch (sectionName) {
      case 'contact':
        return <User className="h-4 w-4" />;
      case 'summary':
        return <FileText className="h-4 w-4" />;
      case 'experience':
        return <Briefcase className="h-4 w-4" />;
      case 'education':
        return <GraduationCap className="h-4 w-4" />;
      case 'skills':
        return <Target className="h-4 w-4" />;
      case 'certifications':
        return <Award className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (present, score) => {
    if (!present) return <XCircle className="h-4 w-4 text-red-500" />;
    if (score >= 80) return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
  };

  const getStatusBadge = (present, score) => {
    if (!present) return <Badge variant="destructive">Missing</Badge>;
    if (score >= 80) return <Badge className="bg-green-100 text-green-700">Good</Badge>;
    if (score >= 60) return <Badge variant="secondary">Needs Work</Badge>;
    return <Badge variant="destructive">Poor</Badge>;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const sectionNames = {
    contact: 'Contact Information',
    summary: 'Professional Summary',
    experience: 'Work Experience',
    education: 'Education',
    skills: 'Skills',
    certifications: 'Certifications'
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <FileText className="h-5 w-5 text-blue-600 mr-2" />
          Resume Sections Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Object.entries(sections).map(([sectionKey, section]) => (
            <div key={sectionKey} className="border rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {getSectionIcon(sectionKey)}
                    <h4 className="font-semibold text-gray-900">
                      {sectionNames[sectionKey] || sectionKey}
                    </h4>
                  </div>
                  {getStatusIcon(section.present, section.score)}
                </div>
                
                <div className="flex items-center space-x-2">
                  {getStatusBadge(section.present, section.score)}
                  {section.present && (
                    <span className={`font-semibold ${getScoreColor(section.score)}`}>
                      {section.score}%
                    </span>
                  )}
                </div>
              </div>

              {section.present && (
                <div>
                  <Progress value={section.score} className="h-2" />
                </div>
              )}

              {section.issues && section.issues.length > 0 && (
                <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
                  <h5 className="text-sm font-medium text-yellow-800 mb-2">Issues to Address:</h5>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    {section.issues.map((issue, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-yellow-500 mr-2">•</span>
                        {issue}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!section.present && (
                <div className="bg-red-50 p-3 rounded border border-red-200">
                  <p className="text-sm text-red-700">
                    This section is missing from your resume. Consider adding it to improve your ATS score.
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SectionsAnalysis;
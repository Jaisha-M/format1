import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { AlertTriangle, XCircle, Info, CheckCircle2, Lightbulb } from 'lucide-react';

const IssuesPanel = ({ analysisResult }) => {
  const getIssueIcon = (type) => {
    switch (type) {
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'info':
        return <Info className="h-4 w-4 text-blue-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getIssueBadgeVariant = (type) => {
    switch (type) {
      case 'critical':
        return 'destructive';
      case 'warning':
        return 'secondary';
      case 'info':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="issues" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="issues">Issues & Fixes</TabsTrigger>
          <TabsTrigger value="keywords">Keywords</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="issues" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-yellow-500 mr-2" />
                Identified Issues ({analysisResult.issues.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysisResult.issues.map((issue, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getIssueIcon(issue.type)}
                      <h4 className="font-semibold text-gray-900">{issue.title}</h4>
                    </div>
                    <Badge variant={getIssueBadgeVariant(issue.type)}>
                      {issue.category}
                    </Badge>
                  </div>
                  
                  <p className="text-gray-600 text-sm">{issue.description}</p>
                  
                  {issue.suggestions && issue.suggestions.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="text-sm font-medium text-gray-700 flex items-center">
                        <Lightbulb className="h-4 w-4 mr-1 text-yellow-500" />
                        Suggestions:
                      </h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {issue.suggestions.map((suggestion, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="text-blue-500 mr-2">•</span>
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="keywords" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Missing Keywords */}
            <Card>
              <CardHeader>
                <CardTitle className="text-red-600 flex items-center">
                  <XCircle className="h-5 w-5 mr-2" />
                  Missing Keywords
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisResult.missingKeywords.map((keyword, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-red-50 rounded">
                      <span className="font-medium">{keyword.keyword}</span>
                      <div className="flex items-center space-x-2">
                        <Badge variant={keyword.importance === 'high' ? 'destructive' : keyword.importance === 'medium' ? 'secondary' : 'outline'}>
                          {keyword.importance}
                        </Badge>
                        <span className="text-xs text-gray-500">×{keyword.frequency}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Found Keywords */}
            <Card>
              <CardHeader>
                <CardTitle className="text-green-600 flex items-center">
                  <CheckCircle2 className="h-5 w-5 mr-2" />
                  Found Keywords
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisResult.foundKeywords.map((keyword, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-green-50 rounded">
                      <span className="font-medium">{keyword.keyword}</span>
                      <div className="flex items-center space-x-2">
                        <Badge variant={keyword.importance === 'high' ? 'default' : 'secondary'}>
                          {keyword.importance}
                        </Badge>
                        <span className="text-xs text-gray-500">×{keyword.frequency}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 text-blue-600 mr-2" />
                Improvement Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {analysisResult.recommendations.map((rec, index) => (
                <div key={index} className={`border rounded-lg p-4 ${getPriorityColor(rec.priority)}`}>
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold">{rec.title}</h4>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">
                        {rec.priority} priority
                      </Badge>
                      <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">
                        {rec.impact}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm opacity-80">{rec.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IssuesPanel;
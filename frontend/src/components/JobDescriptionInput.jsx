import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { FileText, Zap, X } from 'lucide-react';
import { mockJobDescription } from '../data/mock';

const JobDescriptionInput = ({ onJobDescriptionChange, jobDescription }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [localJobDescription, setLocalJobDescription] = useState(jobDescription || '');

  const handleLoadSample = () => {
    setLocalJobDescription(mockJobDescription);
    onJobDescriptionChange(mockJobDescription);
  };

  const handleClear = () => {
    setLocalJobDescription('');
    onJobDescriptionChange('');
  };

  const handleSubmit = () => {
    onJobDescriptionChange(localJobDescription);
    setIsExpanded(false);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="h-5 w-5 text-blue-600 mr-2" />
            Job Description Analysis
          </div>
          {!isExpanded && jobDescription && (
            <Badge variant="secondary" className="bg-green-100 text-green-700">
              ✓ Loaded
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        {!isExpanded && !jobDescription ? (
          <div className="text-center py-6">
            <p className="text-gray-600 mb-4">
              Paste a job description to get personalized keyword recommendations
            </p>
            <Button 
              onClick={() => setIsExpanded(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Zap className="h-4 w-4 mr-2" />
              Add Job Description
            </Button>
          </div>
        ) : !isExpanded && jobDescription ? (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 line-clamp-3">
                {jobDescription.substring(0, 200)}...
              </p>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setIsExpanded(true)}
              >
                Edit
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleClear}
              >
                <X className="h-4 w-4 mr-1" />
                Clear
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <Textarea
              placeholder="Paste the job description here to get personalized keyword recommendations and improve your ATS score..."
              value={localJobDescription}
              onChange={(e) => setLocalJobDescription(e.target.value)}
              className="min-h-[200px] resize-none"
            />
            
            <div className="flex flex-wrap gap-2 justify-between">
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleLoadSample}
                >
                  Load Sample
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleClear}
                >
                  Clear
                </Button>
              </div>
              
              <div className="flex space-x-2">
                <Button 
                  variant="outline"
                  onClick={() => setIsExpanded(false)}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleSubmit}
                  disabled={!localJobDescription.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Analyze Keywords
                </Button>
              </div>
            </div>
            
            <div className="text-xs text-gray-500">
              {localJobDescription.length} / 5000 characters
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default JobDescriptionInput;
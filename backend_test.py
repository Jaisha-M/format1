#!/usr/bin/env python3
"""
Comprehensive Backend Testing for ATS Resume Checker API
Tests all backend endpoints and functionality as specified in the review request.
"""

import requests
import json
import time
import os
import tempfile
from pathlib import Path
import io

# Configuration
BASE_URL = "https://resume-score.preview.emergentagent.com/api"
TIMEOUT = 30

class ATSBackendTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def create_test_pdf(self, content="John Doe\nSoftware Engineer\n\nEXPERIENCE\n• 5 years Python development\n• React and Node.js experience\n• Database design and optimization\n\nEDUCATION\nBachelor of Computer Science\n\nSKILLS\nPython, JavaScript, React, Node.js, MongoDB, SQL, Git, Docker\n\nCONTACT\nEmail: john.doe@email.com\nPhone: (555) 123-4567"):
        """Create a simple fake PDF file for testing"""
        # Create a minimal PDF-like structure for testing
        # This is not a real PDF but will test file upload functionality
        pdf_header = b'%PDF-1.4\n'
        pdf_content = content.encode('utf-8')
        pdf_footer = b'\n%%EOF'
        return pdf_header + pdf_content + pdf_footer
    
    def create_test_text_file(self, content="John Smith\nData Scientist\n\nEXPERIENCE\n- 3 years machine learning\n- Python and R programming\n- Statistical analysis and modeling\n\nEDUCATION\nMaster of Data Science\n\nSKILLS\nPython, R, SQL, TensorFlow, Pandas, Scikit-learn\n\nCONTACT\njohn.smith@email.com\n(555) 987-6543"):
        """Create a test text file"""
        return content.encode('utf-8')
    
    def test_health_check(self):
        """Test 1: Health Check Endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_result("Health Check", True, "API is healthy and responding", {
                        'status_code': response.status_code,
                        'response': data
                    })
                else:
                    self.log_result("Health Check", False, "Health check returned unexpected response", {
                        'status_code': response.status_code,
                        'response': data
                    })
            else:
                self.log_result("Health Check", False, f"Health check failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Health Check", False, f"Health check request failed: {str(e)}")
    
    def test_root_endpoint(self):
        """Test 2: Root API Endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_result("Root Endpoint", True, "Root endpoint responding correctly", {
                        'status_code': response.status_code,
                        'response': data
                    })
                else:
                    self.log_result("Root Endpoint", False, "Root endpoint returned unexpected response", {
                        'status_code': response.status_code,
                        'response': data
                    })
            else:
                self.log_result("Root Endpoint", False, f"Root endpoint failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Root Endpoint", False, f"Root endpoint request failed: {str(e)}")
    
    def test_resume_analysis_valid_pdf(self):
        """Test 3: Resume Analysis with Valid PDF"""
        try:
            pdf_content = self.create_test_pdf()
            
            files = {
                'file': ('test_resume.pdf', pdf_content, 'application/pdf')
            }
            data = {
                'job_description': 'We are looking for a Software Engineer with Python, React, and database experience. Must have 3+ years of development experience.'
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    analysis_data = result['data']
                    required_fields = ['overall_score', 'ats_compatibility', 'keyword_match', 'format_score']
                    
                    if all(field in analysis_data for field in required_fields):
                        self.log_result("Resume Analysis (Valid PDF)", True, "PDF analysis completed successfully", {
                            'status_code': response.status_code,
                            'overall_score': analysis_data.get('overall_score'),
                            'ats_compatibility': analysis_data.get('ats_compatibility'),
                            'keyword_match': analysis_data.get('keyword_match'),
                            'processing_time': analysis_data.get('processing_time')
                        })
                    else:
                        self.log_result("Resume Analysis (Valid PDF)", False, "Analysis response missing required fields", {
                            'status_code': response.status_code,
                            'missing_fields': [f for f in required_fields if f not in analysis_data],
                            'response': result
                        })
                else:
                    self.log_result("Resume Analysis (Valid PDF)", False, "Analysis response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Resume Analysis (Valid PDF)", False, f"PDF analysis failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Resume Analysis (Valid PDF)", False, f"PDF analysis request failed: {str(e)}")
    
    def test_resume_analysis_valid_text(self):
        """Test 4: Resume Analysis with Valid Text File"""
        try:
            text_content = self.create_test_text_file()
            
            files = {
                'file': ('test_resume.txt', text_content, 'text/plain')
            }
            data = {
                'job_description': 'Seeking a Data Scientist with Python, R, and machine learning experience. Statistical analysis skills required.'
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    analysis_data = result['data']
                    required_fields = ['overall_score', 'ats_compatibility', 'keyword_match', 'format_score']
                    
                    if all(field in analysis_data for field in required_fields):
                        self.log_result("Resume Analysis (Valid Text)", True, "Text file analysis completed successfully", {
                            'status_code': response.status_code,
                            'overall_score': analysis_data.get('overall_score'),
                            'ats_compatibility': analysis_data.get('ats_compatibility'),
                            'keyword_match': analysis_data.get('keyword_match')
                        })
                    else:
                        self.log_result("Resume Analysis (Valid Text)", False, "Analysis response missing required fields", {
                            'status_code': response.status_code,
                            'missing_fields': [f for f in required_fields if f not in analysis_data]
                        })
                else:
                    self.log_result("Resume Analysis (Valid Text)", False, "Analysis response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Resume Analysis (Valid Text)", False, f"Text analysis failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Resume Analysis (Valid Text)", False, f"Text analysis request failed: {str(e)}")
    
    def test_resume_analysis_without_job_description(self):
        """Test 5: Resume Analysis without Job Description"""
        try:
            text_content = self.create_test_text_file()
            
            files = {
                'file': ('test_resume.txt', text_content, 'text/plain')
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    self.log_result("Resume Analysis (No Job Description)", True, "Analysis without job description completed", {
                        'status_code': response.status_code,
                        'overall_score': result['data'].get('overall_score')
                    })
                else:
                    self.log_result("Resume Analysis (No Job Description)", False, "Analysis response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Resume Analysis (No Job Description)", False, f"Analysis without JD failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Resume Analysis (No Job Description)", False, f"Analysis without JD request failed: {str(e)}")
    
    def test_invalid_file_type(self):
        """Test 6: Invalid File Type Upload"""
        try:
            # Create a fake image file
            fake_image = b"fake image content"
            
            files = {
                'file': ('test_image.jpg', fake_image, 'image/jpeg')
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files)
            
            if response.status_code == 400:
                self.log_result("Invalid File Type", True, "Invalid file type correctly rejected", {
                    'status_code': response.status_code,
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                })
            else:
                self.log_result("Invalid File Type", False, f"Invalid file type not properly rejected (status: {response.status_code})", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Invalid File Type", False, f"Invalid file type test failed: {str(e)}")
    
    def test_large_file_upload(self):
        """Test 7: Large File Upload (should be rejected)"""
        try:
            # Create a large fake PDF (>10MB)
            large_content = b"fake pdf content" * (1024 * 1024)  # ~16MB
            
            files = {
                'file': ('large_resume.pdf', large_content, 'application/pdf')
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files)
            
            if response.status_code == 400:
                self.log_result("Large File Upload", True, "Large file correctly rejected", {
                    'status_code': response.status_code,
                    'file_size': f"{len(large_content) / (1024*1024):.1f}MB"
                })
            else:
                self.log_result("Large File Upload", False, f"Large file not properly rejected (status: {response.status_code})", {
                    'status_code': response.status_code,
                    'file_size': f"{len(large_content) / (1024*1024):.1f}MB"
                })
                
        except Exception as e:
            self.log_result("Large File Upload", False, f"Large file test failed: {str(e)}")
    
    def test_empty_file_upload(self):
        """Test 8: Empty File Upload"""
        try:
            files = {
                'file': ('empty_resume.pdf', b'', 'application/pdf')
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files)
            
            if response.status_code == 400:
                self.log_result("Empty File Upload", True, "Empty file correctly rejected", {
                    'status_code': response.status_code
                })
            else:
                self.log_result("Empty File Upload", False, f"Empty file not properly rejected (status: {response.status_code})", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Empty File Upload", False, f"Empty file test failed: {str(e)}")
    
    def test_keyword_analysis(self):
        """Test 9: Keyword Analysis API"""
        try:
            payload = {
                'resume_text': 'Software Engineer with 5 years of Python development experience. Skilled in React, Node.js, MongoDB, and Docker. Led team of 3 developers on multiple projects.',
                'job_description': 'We are looking for a Senior Software Engineer with Python, React, and team leadership experience. Docker and MongoDB knowledge preferred.'
            }
            
            response = self.session.post(f"{BASE_URL}/resume/keywords", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    data = result['data']
                    required_fields = ['missing_keywords', 'found_keywords', 'keyword_match']
                    
                    if all(field in data for field in required_fields):
                        self.log_result("Keyword Analysis", True, "Keyword analysis completed successfully", {
                            'status_code': response.status_code,
                            'keyword_match': data.get('keyword_match'),
                            'found_keywords_count': len(data.get('found_keywords', [])),
                            'missing_keywords_count': len(data.get('missing_keywords', []))
                        })
                    else:
                        self.log_result("Keyword Analysis", False, "Keyword analysis response missing required fields", {
                            'status_code': response.status_code,
                            'missing_fields': [f for f in required_fields if f not in data]
                        })
                else:
                    self.log_result("Keyword Analysis", False, "Keyword analysis response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Keyword Analysis", False, f"Keyword analysis failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Keyword Analysis", False, f"Keyword analysis request failed: {str(e)}")
    
    def test_analysis_history(self):
        """Test 10: Analysis History API"""
        try:
            response = self.session.get(f"{BASE_URL}/resume/history")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    data = result['data']
                    required_fields = ['analyses', 'total_count', 'page', 'page_size']
                    
                    if all(field in data for field in required_fields):
                        self.log_result("Analysis History", True, "History retrieval completed successfully", {
                            'status_code': response.status_code,
                            'total_count': data.get('total_count'),
                            'analyses_returned': len(data.get('analyses', [])),
                            'page': data.get('page'),
                            'page_size': data.get('page_size')
                        })
                    else:
                        self.log_result("Analysis History", False, "History response missing required fields", {
                            'status_code': response.status_code,
                            'missing_fields': [f for f in required_fields if f not in data]
                        })
                else:
                    self.log_result("Analysis History", False, "History response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Analysis History", False, f"History retrieval failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Analysis History", False, f"History retrieval request failed: {str(e)}")
    
    def test_analysis_history_pagination(self):
        """Test 11: Analysis History with Pagination"""
        try:
            response = self.session.get(f"{BASE_URL}/resume/history?page=1&page_size=5")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    data = result['data']
                    if data.get('page') == 1 and data.get('page_size') == 5:
                        self.log_result("Analysis History Pagination", True, "Pagination working correctly", {
                            'status_code': response.status_code,
                            'page': data.get('page'),
                            'page_size': data.get('page_size'),
                            'total_count': data.get('total_count')
                        })
                    else:
                        self.log_result("Analysis History Pagination", False, "Pagination parameters not respected", {
                            'status_code': response.status_code,
                            'expected_page': 1,
                            'actual_page': data.get('page'),
                            'expected_page_size': 5,
                            'actual_page_size': data.get('page_size')
                        })
                else:
                    self.log_result("Analysis History Pagination", False, "Pagination response format incorrect", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Analysis History Pagination", False, f"Pagination test failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Analysis History Pagination", False, f"Pagination test request failed: {str(e)}")
    
    def test_database_integration(self):
        """Test 12: Database Integration (verify analysis is saved)"""
        try:
            # First, perform an analysis
            text_content = self.create_test_text_file("Database Test Resume\nSoftware Developer\n\nEXPERIENCE\n• Database design\n• API development\n\nSKILLS\nPython, SQL, MongoDB")
            
            files = {
                'file': ('db_test_resume.txt', text_content, 'text/plain')
            }
            data = {
                'job_description': 'Database developer position requiring SQL and MongoDB experience.'
            }
            
            # Perform analysis
            analysis_response = self.session.post(f"{BASE_URL}/resume/analyze", files=files, data=data)
            
            if analysis_response.status_code == 200:
                # Wait a moment for database write
                time.sleep(2)
                
                # Check if it appears in history
                history_response = self.session.get(f"{BASE_URL}/resume/history")
                
                if history_response.status_code == 200:
                    history_result = history_response.json()
                    if history_result.get('success') and 'data' in history_result:
                        total_count = history_result['data'].get('total_count', 0)
                        analyses = history_result['data'].get('analyses', [])
                        
                        # Check if our analysis is in the recent analyses
                        recent_analysis = None
                        for analysis in analyses:
                            if 'db_test_resume.txt' in analysis.get('file_name', ''):
                                recent_analysis = analysis
                                break
                        
                        if recent_analysis:
                            self.log_result("Database Integration", True, "Analysis successfully saved and retrieved from database", {
                                'total_analyses': total_count,
                                'analysis_id': recent_analysis.get('id'),
                                'file_name': recent_analysis.get('file_name')
                            })
                        else:
                            self.log_result("Database Integration", False, "Analysis not found in database history", {
                                'total_analyses': total_count,
                                'recent_files': [a.get('file_name') for a in analyses[:3]]
                            })
                    else:
                        self.log_result("Database Integration", False, "Could not retrieve history to verify database save", {
                            'history_response': history_result
                        })
                else:
                    self.log_result("Database Integration", False, f"History retrieval failed with status {history_response.status_code}")
            else:
                self.log_result("Database Integration", False, f"Initial analysis failed with status {analysis_response.status_code}")
                
        except Exception as e:
            self.log_result("Database Integration", False, f"Database integration test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test 13: Error Handling for Various Scenarios"""
        try:
            # Test 1: No file provided
            response1 = self.session.post(f"{BASE_URL}/resume/analyze")
            error1_handled = response1.status_code in [400, 422]
            
            # Test 2: Invalid keyword analysis request
            response2 = self.session.post(f"{BASE_URL}/resume/keywords", json={})
            error2_handled = response2.status_code in [400, 422]
            
            # Test 3: Invalid history page
            response3 = self.session.get(f"{BASE_URL}/resume/history?page=-1")
            error3_handled = response3.status_code in [200, 400, 422]  # May handle gracefully
            
            errors_handled = sum([error1_handled, error2_handled, error3_handled])
            
            if errors_handled >= 2:
                self.log_result("Error Handling", True, f"Error handling working correctly ({errors_handled}/3 scenarios)", {
                    'no_file_status': response1.status_code,
                    'invalid_keywords_status': response2.status_code,
                    'invalid_page_status': response3.status_code
                })
            else:
                self.log_result("Error Handling", False, f"Error handling needs improvement ({errors_handled}/3 scenarios)", {
                    'no_file_status': response1.status_code,
                    'invalid_keywords_status': response2.status_code,
                    'invalid_page_status': response3.status_code
                })
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Error handling test failed: {str(e)}")
    
    def test_response_validation(self):
        """Test 14: Response Schema Validation"""
        try:
            text_content = self.create_test_text_file()
            
            files = {
                'file': ('schema_test.txt', text_content, 'text/plain')
            }
            data = {
                'job_description': 'Test job description for schema validation.'
            }
            
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    analysis_data = result['data']
                    
                    # Check required fields and their types
                    schema_checks = {
                        'id': str,
                        'file_name': str,
                        'overall_score': int,
                        'ats_compatibility': int,
                        'keyword_match': int,
                        'format_score': int,
                        'issues': list,
                        'missing_keywords': list,
                        'found_keywords': list,
                        'sections': dict,
                        'recommendations': list
                    }
                    
                    schema_valid = True
                    invalid_fields = []
                    
                    for field, expected_type in schema_checks.items():
                        if field not in analysis_data:
                            schema_valid = False
                            invalid_fields.append(f"{field} missing")
                        elif not isinstance(analysis_data[field], expected_type):
                            schema_valid = False
                            invalid_fields.append(f"{field} wrong type (expected {expected_type.__name__}, got {type(analysis_data[field]).__name__})")
                    
                    # Check score ranges
                    score_fields = ['overall_score', 'ats_compatibility', 'keyword_match', 'format_score']
                    for field in score_fields:
                        if field in analysis_data:
                            score = analysis_data[field]
                            if not (0 <= score <= 100):
                                schema_valid = False
                                invalid_fields.append(f"{field} out of range (0-100): {score}")
                    
                    if schema_valid:
                        self.log_result("Response Schema Validation", True, "All response fields match expected schema", {
                            'status_code': response.status_code,
                            'fields_checked': len(schema_checks)
                        })
                    else:
                        self.log_result("Response Schema Validation", False, "Response schema validation failed", {
                            'status_code': response.status_code,
                            'invalid_fields': invalid_fields
                        })
                else:
                    self.log_result("Response Schema Validation", False, "Response format incorrect for schema validation", {
                        'status_code': response.status_code,
                        'response': result
                    })
            else:
                self.log_result("Response Schema Validation", False, f"Schema validation test failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'response': response.text
                })
                
        except Exception as e:
            self.log_result("Response Schema Validation", False, f"Schema validation test failed: {str(e)}")
    
    def test_processing_time_monitoring(self):
        """Test 15: Processing Time Monitoring"""
        try:
            text_content = self.create_test_text_file()
            
            files = {
                'file': ('timing_test.txt', text_content, 'text/plain')
            }
            data = {
                'job_description': 'Performance test job description with various keywords for timing analysis.'
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/resume/analyze", files=files, data=data)
            end_time = time.time()
            
            request_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    processing_time = result['data'].get('processing_time')
                    
                    # Check if processing time is reasonable (< 30 seconds)
                    if request_time < 30:
                        self.log_result("Processing Time Monitoring", True, "Processing time within acceptable limits", {
                            'status_code': response.status_code,
                            'request_time': f"{request_time:.2f}s",
                            'reported_processing_time': f"{processing_time:.2f}s" if processing_time else "Not reported"
                        })
                    else:
                        self.log_result("Processing Time Monitoring", False, "Processing time too slow", {
                            'status_code': response.status_code,
                            'request_time': f"{request_time:.2f}s",
                            'threshold': "30s"
                        })
                else:
                    self.log_result("Processing Time Monitoring", False, "Could not verify processing time due to response format", {
                        'status_code': response.status_code,
                        'request_time': f"{request_time:.2f}s"
                    })
            else:
                self.log_result("Processing Time Monitoring", False, f"Processing time test failed with status {response.status_code}", {
                    'status_code': response.status_code,
                    'request_time': f"{request_time:.2f}s"
                })
                
        except Exception as e:
            self.log_result("Processing Time Monitoring", False, f"Processing time test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting ATS Resume Checker Backend Tests")
        print(f"📍 Testing API at: {BASE_URL}")
        print("=" * 60)
        
        # Run all tests
        test_methods = [
            self.test_health_check,
            self.test_root_endpoint,
            self.test_resume_analysis_valid_pdf,
            self.test_resume_analysis_valid_text,
            self.test_resume_analysis_without_job_description,
            self.test_invalid_file_type,
            self.test_large_file_upload,
            self.test_empty_file_upload,
            self.test_keyword_analysis,
            self.test_analysis_history,
            self.test_analysis_history_pagination,
            self.test_database_integration,
            self.test_error_handling,
            self.test_response_validation,
            self.test_processing_time_monitoring
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.results
        }

if __name__ == "__main__":
    tester = ATSBackendTester()
    summary = tester.run_all_tests()
    
    # Save results to file
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: /app/backend_test_results.json")
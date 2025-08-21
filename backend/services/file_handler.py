import os
import aiofiles
import uuid
from pathlib import Path
from typing import Tuple
import mimetypes
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self):
        # Create uploads directory if it doesn't exist
        self.upload_dir = Path("/tmp/resume_uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Allowed file types and their extensions
        self.allowed_types = {
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/plain': '.txt',
            # Add more lenient content type matching
            'application/octet-stream': '.pdf'  # Some browsers send PDFs as this
        }
        
        # Maximum file size (10MB)
        self.max_file_size = 10 * 1024 * 1024
    
    async def save_uploaded_file(self, file_content: bytes, filename: str, content_type: str) -> Tuple[str, str]:
        """Save uploaded file and return file path and detected type"""
        try:
            # Validate file type
            if content_type not in self.allowed_types:
                raise ValueError(f"Unsupported file type: {content_type}")
            
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB")
            
            if len(file_content) == 0:
                raise ValueError("Empty file uploaded")
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = self.get_file_extension(filename, content_type)
            safe_filename = f"{file_id}{file_extension}"
            
            file_path = self.upload_dir / safe_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"File saved: {file_path}")
            
            # Determine file type for parser
            file_type = self.get_file_type(content_type, filename)
            
            return str(file_path), file_type
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise e
    
    def get_file_extension(self, filename: str, content_type: str) -> str:
        """Get appropriate file extension"""
        # First try to get extension from content type
        if content_type in self.allowed_types:
            return self.allowed_types[content_type]
        
        # Fallback to filename extension
        _, ext = os.path.splitext(filename.lower())
        if ext in ['.pdf', '.doc', '.docx', '.txt']:
            return ext
        
        # Default fallback
        return '.pdf'
    
    def get_file_type(self, content_type: str, filename: str) -> str:
        """Determine file type for parser"""
        if 'pdf' in content_type.lower() or filename.lower().endswith('.pdf'):
            return 'pdf'
        elif 'wordprocessingml' in content_type.lower() or filename.lower().endswith('.docx'):
            return 'docx'
        elif 'msword' in content_type.lower() or filename.lower().endswith('.doc'):
            return 'doc'
        elif 'text' in content_type.lower() or filename.lower().endswith('.txt'):
            return 'txt'
        else:
            return 'pdf'  # Default assumption
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old uploaded files"""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path}")
                        
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def validate_file(self, file_content: bytes, filename: str, content_type: str) -> bool:
        """Validate uploaded file"""
        try:
            # Check file size
            if len(file_content) == 0:
                raise ValueError("File is empty")
            
            if len(file_content) > self.max_file_size:
                raise ValueError(f"File too large (max {self.max_file_size // (1024*1024)}MB)")
            
            # Check content type - be more lenient
            valid_types = list(self.allowed_types.keys())
            
            # Check if content type is allowed OR if we can determine from filename
            is_valid_content_type = content_type in valid_types
            
            # If content type is not recognized, try to guess from filename
            if not is_valid_content_type:
                guessed_type, _ = mimetypes.guess_type(filename)
                if guessed_type and guessed_type in valid_types:
                    is_valid_content_type = True
                elif filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                    is_valid_content_type = True
            
            if not is_valid_content_type:
                raise ValueError(f"Unsupported file type: {content_type}. Supported types: PDF, DOC, DOCX, TXT")
            
            # Basic file content validation
            if filename.lower().endswith('.pdf') or content_type == 'application/pdf':
                # PDF files should start with %PDF
                if not file_content.startswith(b'%PDF'):
                    # Allow files that might be PDFs but have different headers
                    logger.warning(f"PDF file doesn't have standard header, but proceeding: {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            raise e
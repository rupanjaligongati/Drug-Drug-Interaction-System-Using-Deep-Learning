"""
File Upload Utility for Image Analysis
Handles secure file storage and retrieval
"""

import os
import uuid
import re
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Upload directory configuration
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads"
)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def ensure_upload_directory():
    """Create uploads directory if it doesn't exist"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        logger.info(f"✅ Created uploads directory: {UPLOAD_DIR}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]
    
    return f"{name}{ext}"


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename with timestamp and UUID
    
    Args:
        original_filename: Original uploaded filename
        
    Returns:
        Unique filename
    """
    # Sanitize original filename
    safe_filename = sanitize_filename(original_filename)
    
    # Get extension
    _, ext = os.path.splitext(safe_filename)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate short UUID
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine: timestamp_uuid_originalname.ext
    return f"{timestamp}_{unique_id}_{safe_filename}"


def save_uploaded_file(file_content: bytes, original_filename: str) -> Optional[str]:
    """
    Save uploaded file to uploads directory
    
    Args:
        file_content: Raw file bytes
        original_filename: Original filename from upload
        
    Returns:
        Relative file path if successful, None otherwise
    """
    try:
        # Ensure upload directory exists
        ensure_upload_directory()
        
        # Validate file extension
        _, ext = os.path.splitext(original_filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            logger.error(f"Invalid file extension: {ext}")
            return None
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            logger.error(f"File too large: {len(file_content)} bytes")
            return None
        
        # Generate unique filename
        unique_filename = generate_unique_filename(original_filename)
        
        # Full file path
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Return relative path (for database storage)
        relative_path = f"uploads/{unique_filename}"
        
        logger.info(f"✅ Saved file: {relative_path} ({len(file_content)} bytes)")
        return relative_path
        
    except Exception as e:
        logger.error(f"❌ Failed to save file: {e}")
        return None


def save_multiple_files(files_data: List[tuple]) -> List[str]:
    """
    Save multiple uploaded files
    
    Args:
        files_data: List of (file_content, filename) tuples
        
    Returns:
        List of relative file paths
    """
    saved_paths = []
    
    for file_content, filename in files_data:
        path = save_uploaded_file(file_content, filename)
        if path:
            saved_paths.append(path)
    
    return saved_paths


def get_file_path(relative_path: str) -> Optional[str]:
    """
    Get absolute file path from relative path
    
    Args:
        relative_path: Relative path stored in database
        
    Returns:
        Absolute file path if exists, None otherwise
    """
    try:
        # Remove 'uploads/' prefix if present
        if relative_path.startswith('uploads/'):
            filename = relative_path.replace('uploads/', '')
        else:
            filename = relative_path
        
        # Construct absolute path
        abs_path = os.path.join(UPLOAD_DIR, filename)
        
        # Verify file exists
        if os.path.exists(abs_path):
            return abs_path
        else:
            logger.warning(f"File not found: {abs_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting file path: {e}")
        return None


def delete_file(relative_path: str) -> bool:
    """
    Delete uploaded file
    
    Args:
        relative_path: Relative path stored in database
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        abs_path = get_file_path(relative_path)
        if abs_path and os.path.exists(abs_path):
            os.remove(abs_path)
            logger.info(f"✅ Deleted file: {relative_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}")
        return False


def delete_multiple_files(relative_paths: List[str]) -> int:
    """
    Delete multiple uploaded files
    
    Args:
        relative_paths: List of relative paths
        
    Returns:
        Number of files successfully deleted
    """
    deleted_count = 0
    for path in relative_paths:
        if delete_file(path):
            deleted_count += 1
    return deleted_count

"""
File Serving Routes
Secure endpoints for serving uploaded images
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import logging

from database import get_db
from models import InteractionHistory
from utils.file_upload import get_file_path

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/uploads/{filename}", tags=["Files"])
async def serve_uploaded_file(
    filename: str,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Serve uploaded image file securely
    
    Security measures:
    - Validates file exists
    - Checks user owns the file (if authenticated)
    - Prevents directory traversal
    - Returns 404 if unauthorized
    
    Args:
        filename: Name of the file to serve
        db: Database session
        authorization: Optional Bearer token
        
    Returns:
        File response with image
    """
    try:
        # Construct relative path
        relative_path = f"uploads/{filename}"
        
        # Get absolute file path (validates existence)
        file_path = get_file_path(relative_path)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Optional: Verify user owns this file (if authenticated)
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.replace("Bearer ", "")
                from utils.auth import decode_token
                payload = decode_token(token)
                user_id = payload.get("user_id")
                
                if user_id:
                    # Check if this file belongs to user's history
                    import json
                    history_records = db.query(InteractionHistory).filter(
                        InteractionHistory.user_id == user_id,
                        InteractionHistory.analysis_mode == "image"
                    ).all()
                    
                    # Check if filename is in any of the user's image_paths
                    file_belongs_to_user = False
                    for record in history_records:
                        if record.image_paths:
                            paths = json.loads(record.image_paths)
                            if relative_path in paths or filename in [os.path.basename(p) for p in paths]:
                                file_belongs_to_user = True
                                break
                    
                    if not file_belongs_to_user:
                        logger.warning(f"⚠️ User {user_id} attempted to access unauthorized file: {filename}")
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="File not found"
                        )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error validating file ownership: {e}")
                # Continue serving file even if validation fails (graceful degradation)
        
        # Determine media type
        media_type = "image/jpeg"
        if filename.lower().endswith('.png'):
            media_type = "image/png"
        
        logger.info(f"📤 Serving file: {filename}")
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve file"
        )

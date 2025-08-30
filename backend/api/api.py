# coding=utf-8

import os
import datetime
import tempfile
import shutil
import urllib.parse

from pydantic import BaseModel
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.services import DuplicateService


app = FastAPI(title="Duplicate Content Detection API",
              description="API for detecting duplicate content in documents",
              version="1.0.0")

# NOTE: Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the duplicate service for concurrent processing
duplicate_service = DuplicateService(max_workers=4)

class DuplicateCheckResponse(BaseModel):
    message: str
    output_path: str
    download_url: str


@app.post("/api/v1/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate_content_sync(
        file: UploadFile = File(...),
        output_path: Optional[str] = None
):
    """
    ```
    Check for duplicate content in an uploaded file.
    
    Args:
        file: The document file to check for duplicates
        output_path: Optional path where the result markdown file should be saved
    
    Returns:
        DuplicateCheckResponse: Information about the processing result
    ```
    """
    # Create a temporary file to store the uploaded content
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        # Save the uploaded file to a temporary location
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file_path = tmp_file.name

    # Define result_output_path in the correct scope
    if output_path is None:
        # Get the base name of the temporary file without extension
        base_name = os.path.splitext(os.path.basename(tmp_file_path))[0]
        # Get the directory of the temporary file
        tmp_dir = os.path.dirname(tmp_file_path)
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Construct new output path: directory + base_name + timestamp + .md
        result_output_path = os.path.join(tmp_dir, f"{base_name}_{timestamp}.md")
    else:
        result_output_path = output_path
    
    try:
        # Process the file for duplicate content using the service
        duplicate_service.process_file_sync(tmp_file_path, result_output_path)
        
        # Create download URL
        encoded_path = urllib.parse.quote(result_output_path)
        download_url = f"/api/v1/download-result/{encoded_path}"
        
        return DuplicateCheckResponse(
            message="Duplicate content check completed successfully",
            output_path=result_output_path,
            download_url=download_url
        )
    except Exception as e:
        # Clean up temporary files in case of error
        try:
            os.unlink(tmp_file_path)
            if output_path and os.path.exists(result_output_path):
                os.unlink(result_output_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary input file
        try:
            os.unlink(tmp_file_path)
        except:
            pass


@app.post("/api/v1/duplicate-check-async", response_model=DuplicateCheckResponse)
async def check_duplicate_content_async(
        file: UploadFile = File(...),
        output_path: Optional[str] = None
):
    """
    ```
    Asynchronously check for duplicate content in an uploaded file with concurrent processing.
    
    Args:
        file: The document file to check for duplicates
        output_path: Optional path where the result markdown file should be saved
    
    Returns:
        DuplicateCheckResponse: Information about the processing result
    ```
    """
    # Create a temporary file to store the uploaded content
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        # Save the uploaded file to a temporary location
        shutil.copyfileobj(file.file, tmp_file)
        tmp_file_path = tmp_file.name

    # Define result_output_path in the correct scope
    if output_path is None:
        # Get the base name of the temporary file without extension
        base_name = os.path.splitext(os.path.basename(tmp_file_path))[0]
        # Get the directory of the temporary file
        tmp_dir = os.path.dirname(tmp_file_path)
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Construct new output path: directory + base_name + timestamp + .md
        result_output_path = os.path.join(tmp_dir, f"{base_name}_{timestamp}.md")
    else:
        result_output_path = output_path
    
    try:
        # Process the file for duplicate content asynchronously
        await duplicate_service.process_file_async(tmp_file_path, result_output_path)
        
        # Create download URL
        encoded_path = urllib.parse.quote(result_output_path)
        download_url = f"/api/v1/download-result/{encoded_path}"
        
        return DuplicateCheckResponse(
            message="Duplicate content check completed successfully",
            output_path=result_output_path,
            download_url=download_url
        )
    except Exception as e:
        # Clean up temporary files in case of error
        try:
            os.unlink(tmp_file_path)
            if output_path and os.path.exists(result_output_path):
                os.unlink(result_output_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary input file
        try:
            os.unlink(tmp_file_path)
        except:
            pass


@app.get("/api/v1/download-result/{file_path}")
async def download_result(file_path: str):
    """
    ```
    Download the result file.
    
    Args:
        file_path: Path to the result file
    
    Returns:
        FileResponse: The result file for download
    ```
    """
    # Decode URL encoded file path
    decoded_path = urllib.parse.unquote(file_path)
    
    # Check if file exists
    if not os.path.exists(decoded_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Extract filename for the download header
    filename = os.path.basename(decoded_path)
    
    # Return file response with background cleanup task
    return FileResponse(
        path=decoded_path,
        filename=filename,
        media_type='text/markdown'
    )
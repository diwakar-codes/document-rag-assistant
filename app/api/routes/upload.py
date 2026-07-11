from pathlib import Path 
from app.services.document_service import DocumentService
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.upload_schema import UploadResponse
from app.services.file_service import FileService

router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB MAX

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}

@router.post("/")
async def upload_documents(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )
    
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File exceeds the 10 MB limit."
        )

    file.file.seek(0)

    saved_path = FileService.save_file(file)
    document = DocumentService.extract(saved_path)


    return {
        "original_filename": file.filename,
        "stored_filename": saved_path.name,
        "file_type": extension,
        "size": saved_path.stat().st_size,
        "document": document,
    }

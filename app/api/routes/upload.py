from pathlib import Path 
from app.services.document_service import DocumentService
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.chunk_service import ChunkService
from app.schemas.upload_schema import UploadResponse
from app.services.file_service import FileService
from app.services.embedding_service import EmbeddingService

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
    chunks = ChunkService.split(document)
    embedded_chunks = EmbeddingService.embed_chunks(chunks)

    return {
    "total_chunks": len(embedded_chunks),
    "embedding_dimension": len(embedded_chunks[0]["embedding"]),
    "sample_chunk": embedded_chunks[0]
    }
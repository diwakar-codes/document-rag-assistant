from pathlib import Path 
from app.services.document_service import DocumentService
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.chunk_service import ChunkService
from app.schemas.upload_schema import UploadResponse
from app.services.file_service import FileService
from app.services.embedding_service import EmbeddingService
from app.services.pinecone_service import PineconeService
from app.services.store_service import StoreService
import uuid

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

    document_id = str(uuid.uuid4())
    saved_path = FileService.save_file(file)
    document = DocumentService.extract(
        file_path = saved_path,
        document_id=document_id,
        filename=file.filename,    
    )
    chunks = ChunkService.split(document=document, document_id=document_id,filename=file.filename,)
    embedded_chunks = EmbeddingService.embed_chunks(chunks)
    pinecone = PineconeService()
    pinecone.upsert_chunks(embedded_chunks)

    StoreService.add_document(
        document_id=document_id,
        filename=file.filename,
        file_type=extension,
        total_pages=document.get("total_pages", 1),
        extraction_method=document.get("extraction_method", "pdfplumber"),
    )
    StoreService.add_chunks(document_id, chunks)

    return {
        "message": "Document indexed successfully.",
        "document_id": document_id,
        "chunks": len(embedded_chunks),
    }
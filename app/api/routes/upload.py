import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.file_service import BASE_UPLOAD_DIR, FileService
from app.services.pinecone_service import PineconeService
from app.services.store_service import StoreService
from app.services.topic_service import TopicService

router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB MAX

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


class PageText(BaseModel):
    page: int
    text: str


class ConfirmUploadRequest(BaseModel):
    document_id: str
    filename: str
    extension: str
    extraction_method: str
    pages: List[PageText]


def _validate_and_save(file: UploadFile):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    content = file.file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds the 10 MB limit.")

    file.file.seek(0)

    saved_path = FileService.save_file(file)

    return extension, saved_path


def _index_document(
    document_id: str,
    filename: str,
    extension: str,
    extraction_method: str,
    pages: list,
):
    document = {
        "total_pages": len(pages),
        "pages": pages,
    }

    chunks = ChunkService.split(
        document=document,
        document_id=document_id,
        filename=filename,
    )
    chunks = TopicService.assign_topics(chunks)
    embedded_chunks = EmbeddingService.embed_chunks(chunks)

    pinecone = PineconeService()
    pinecone.upsert_chunks(embedded_chunks)

    StoreService.add_document(
        document_id=document_id,
        filename=filename,
        file_type=extension,
        total_pages=len(pages),
        extraction_method=extraction_method,
    )
    StoreService.add_chunks(document_id, chunks)

    return {
        "message": "Document indexed successfully.",
        "document_id": document_id,
        "chunks": len(embedded_chunks),
    }


@router.post("/")
def upload_documents(file: UploadFile = File(...)):
    extension, saved_path = _validate_and_save(file)

    document_id = str(uuid.uuid4())
    document = DocumentService.extract(
        file_path=saved_path,
        document_id=document_id,
        filename=file.filename,
    )

    return _index_document(
        document_id=document_id,
        filename=file.filename,
        extension=extension,
        extraction_method=document.get("extraction_method", "pdfplumber"),
        pages=document["pages"],
    )


@router.post("/preview")
def preview_upload(file: UploadFile = File(...)):
    """
    Extract text (running OCR if needed) without indexing yet, so the
    caller can review/correct the extracted text before it is embedded.
    """

    extension, saved_path = _validate_and_save(file)

    document_id = str(uuid.uuid4())
    document = DocumentService.extract(
        file_path=saved_path,
        document_id=document_id,
        filename=file.filename,
    )

    image_url: Optional[str] = None
    if extension != ".pdf":
        image_url = f"/files/{saved_path.relative_to(BASE_UPLOAD_DIR).as_posix()}"

    return {
        "document_id": document_id,
        "filename": file.filename,
        "extension": extension,
        "extraction_method": document.get("extraction_method", "pdfplumber"),
        "total_pages": document["total_pages"],
        "pages": document["pages"],
        "image_url": image_url,
    }


@router.post("/confirm")
def confirm_upload(request: ConfirmUploadRequest):
    """Index a document previously extracted via /upload/preview, using
    the (possibly user-corrected) page text supplied in the request."""

    return _index_document(
        document_id=request.document_id,
        filename=request.filename,
        extension=request.extension,
        extraction_method=request.extraction_method,
        pages=[page.model_dump() for page in request.pages],
    )

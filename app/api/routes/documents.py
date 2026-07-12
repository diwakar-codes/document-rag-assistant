from fastapi import APIRouter, HTTPException

from app.services.pinecone_service import PineconeService
from app.services.store_service import StoreService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents():
    return StoreService.list_documents()


@router.get("/{document_id}")
def get_document(document_id: str):
    document = StoreService.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {
        **document,
        "chunks": StoreService.list_chunks(document_id=document_id),
    }


@router.delete("/{document_id}")
def delete_document(document_id: str):
    document = StoreService.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    StoreService.delete_document(document_id)

    try:
        PineconeService().delete_by_document(document_id)
    except Exception:
        pass

    return {"message": "Document deleted."}

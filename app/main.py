from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.services.file_service import BASE_UPLOAD_DIR
from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.topics import router as topics_router


app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
)

@app.get('/')
def health():
    return {"status": "healthy"}

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(topics_router)

app.mount("/files", StaticFiles(directory=str(BASE_UPLOAD_DIR)), name="files")
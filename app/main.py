from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from groq import APIStatusError

from app.core.config import settings
from app.services.file_service import BASE_UPLOAD_DIR
from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.topics import router as topics_router
from app.api.routes.quiz import router as quiz_router
from app.api.routes.study import router as study_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.system import router as system_router


app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
)

@app.get('/')
def health():
    return {"status": "healthy"}


@app.exception_handler(APIStatusError)
def groq_api_error_handler(request: Request, exc: APIStatusError):
    status_code = getattr(exc, "status_code", 503) or 503

    detail = "The AI provider (Groq) returned an error."
    if status_code == 429:
        detail = "Groq rate limit reached. Please wait a bit and try again."

    return JSONResponse(status_code=status_code, content={"detail": detail})

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(topics_router)
app.include_router(quiz_router)
app.include_router(study_router)
app.include_router(analytics_router)
app.include_router(system_router)

app.mount("/files", StaticFiles(directory=str(BASE_UPLOAD_DIR)), name="files")
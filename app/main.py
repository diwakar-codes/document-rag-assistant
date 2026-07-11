from fastapi import FastAPI 
from app.core.config import settings
from app.api.routes.upload import router as upload_router


app = FastAPI(
    title = settings.APP_NAME,
    version = settings.APP_VERSION,
)

@app.get('/')
def health():
    return {"status": "healthy"}

app.include_router(upload_router)

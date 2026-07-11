from pydantic import BaseModel

# validating the user upload
class UploadResponse(BaseModel):
    original_filename: str
    stored_filename: str
    file_type: str
    size: int
    message: str


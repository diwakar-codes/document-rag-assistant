from pathlib import Path
import shutil
import uuid

BASE_UPLOAD_DIR = Path("app/uploads")

PDF_DIR = BASE_UPLOAD_DIR / "pdf"
IMAGE_DIR = BASE_UPLOAD_DIR / "images"

PDF_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIRECTORIES = {
    ".pdf": PDF_DIR,
    ".jpg": IMAGE_DIR,
    ".jpeg": IMAGE_DIR,
    ".png": IMAGE_DIR,
}

class FileService:

    @staticmethod
    def save_file(file):
        extension = Path(file.filename).suffix.lower()

        upload_dir = UPLOAD_DIRECTORIES.get(extension)
        if upload_dir is None:
            raise ValueError("Unsupported file type.")

        unique_filename = f"{uuid.uuid4()}{extension}"

        file_path = upload_dir / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path
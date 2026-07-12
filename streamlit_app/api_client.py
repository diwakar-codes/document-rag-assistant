import os
import urllib.parse

import requests

BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 120


class APIError(Exception):
    pass


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def _request(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, _url(path), timeout=TIMEOUT, **kwargs)
        response.raise_for_status()
        if response.content:
            return response.json()
        return None
    except requests.exceptions.RequestException as exc:
        detail = str(exc)
        try:
            detail = exc.response.json().get("detail", detail)
        except Exception:
            pass
        raise APIError(detail) from exc


def health_check() -> bool:
    try:
        requests.get(_url("/"), timeout=5).raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def system_info():
    return _request("GET", "/system/info")


def list_documents():
    return _request("GET", "/documents/")


def get_document(document_id: str):
    return _request("GET", f"/documents/{document_id}")


def delete_document(document_id: str):
    return _request("DELETE", f"/documents/{document_id}")


def upload_document(filename: str, file_bytes: bytes, mime_type: str):
    files = {"file": (filename, file_bytes, mime_type)}
    return _request("POST", "/upload/", files=files)


def preview_upload(filename: str, file_bytes: bytes, mime_type: str):
    files = {"file": (filename, file_bytes, mime_type)}
    return _request("POST", "/upload/preview", files=files)


def confirm_upload(payload: dict):
    return _request("POST", "/upload/confirm", json=payload)


def file_url(path: str) -> str:
    return _url(path)


def chat(payload: dict):
    return _request("POST", "/chat/", json=payload)


def clear_chat():
    return _request("POST", "/chat/clear")


def list_topics():
    return _request("GET", "/topics/")


def topic_summary(topic: str):
    return _request("GET", f"/topics/{urllib.parse.quote(topic)}/summary")


def generate_quiz(payload: dict):
    return _request("POST", "/quiz/generate", json=payload)


def evaluate_quiz(payload: dict):
    return _request("POST", "/quiz/evaluate", json=payload)


def generate_flashcards(payload: dict):
    return _request("POST", "/flashcards/generate", json=payload)


def generate_study_plan(payload: dict):
    return _request("POST", "/study/plan", json=payload)


def get_analytics():
    return _request("GET", "/analytics/")

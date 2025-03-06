import tempfile
from enum import StrEnum
from pathlib import Path

CACHE_FOLDER = Path(tempfile.gettempdir()) / "pdf2u_cache"


def get_cache_file_path(filename: str) -> Path:
    return CACHE_FOLDER / filename


class TranslationService(StrEnum):
    OPENAI: str = "openai"
    GOOGLE: str = "google"
    BING: str = "bing"

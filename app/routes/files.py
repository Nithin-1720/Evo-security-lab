from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS = ROOT / "lab-data" / "documents"


@router.get("/", response_class=PlainTextResponse)
def read_file(filename: str):

    # INTENTIONALLY VULNERABLE.
    file_path = DOCUMENTS / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
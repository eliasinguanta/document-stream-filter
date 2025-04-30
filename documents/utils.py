from pydantic import BaseModel
from typing import List
from datetime import datetime

class Document(BaseModel):
    documentName: str
    size: int
    mimeType: str
    uploadDate: datetime
    words: List[str]
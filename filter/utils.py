from pydantic import BaseModel
from typing import List
from datetime import datetime

class Query(BaseModel):
    queryId: int
    word: str
    metric: str
    distance: int

class Document(BaseModel):
    documentName: str
    size: int
    mimeType: str
    uploadDate: datetime
    words: List[str]
    
class Match(BaseModel):
    query: Query
    results: list[Document]
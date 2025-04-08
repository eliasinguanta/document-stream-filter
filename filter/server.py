from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Document(BaseModel):
    documentName: str  # Name of the document (e.g. 'document1.txt')
    size: int          # Size of the document in bytes
    mimeType: str      # MIME type (e.g. 'text/plain')
    uploadDate: str    # Upload date (e.g. '2023-10-01')
    words: List[str]   # List of words in the document

class Query(BaseModel):
    queryId: int       # Identifier for the query (needed for the backend database)
    word: str          # Searched word (e.g. 'hello')
    metric: str        # The metric (e.g. 'edit')
    distance: int      # Distance for the metric (e.g. 2)

class FilterRequest(BaseModel):
    queries: List[Query]
    documents: List[Document]

@app.get("/health")
def health_check():
    return {"status": "ok"}
    
# Endpoint for filtering documents based on queries
# TODO: Expand metric to edit and hamming
@app.post("/filter")
def filter_docs(data: FilterRequest):
    results = []

    # Iterate over each query and each document
    for query in data.queries:
        matched = []
        for doc in data.documents:
            
            # check if the word is in the document
            if query.word.lower() in [word.lower() for word in doc.words]:  
                matched.append(doc)
        
        results.append({
            "query": query,
            "results": matched
        })
    
    return results

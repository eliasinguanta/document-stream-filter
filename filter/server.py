from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode, array_contains

app = FastAPI()

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("document-stream-filter") \
    .master("k8s://https://F9803F8F3EE6F9E63903294AC34C965F.gr7.eu-north-1.eks.amazonaws.com") \
    .config("spark.kubernetes.container.image", "386757133985.dkr.ecr.eu-north-1.amazonaws.com/dsf-filter:latest") \
    .config("spark.kubernetes.namespace", "document-stream-filter") \
    .config("spark.executor.instances", "10") \
    .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()


# Spark Session init
spark = SparkSession.builder \
    .appName("document-stream-filter") \
    .getOrCreate()

class Document(BaseModel):
    documentName: str
    size: int
    mimeType: str
    uploadDate: str
    words: List[str]

class Query(BaseModel):
    queryId: int
    word: str
    metric: str
    distance: int

class FilterRequest(BaseModel):
    queries: List[Query]
    documents: List[Document]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/filter")
def filter_docs(data: FilterRequest):
    # Create a Spark DataFrame from the documents
    docs_rdd = spark.sparkContext.parallelize([doc.dict() for doc in data.documents])
    docs_df = spark.read.json(docs_rdd)

    # Lowercase all words
    docs_df = docs_df.withColumn("words", 
        explode("words")) \
        .withColumn("words", lower(col("words")))

    results = []

    for query in data.queries:
        # filter documents that contain the word
        filtered = docs_df.filter(col("words") == query.word.lower())
        
        # group by document
        docs_filtered = filtered.groupBy("documentName", "size", "mimeType", "uploadDate") \
                                .count() \
                                .drop("count")

        result_docs = docs_filtered.collect()
        results.append({
            "query": query.dict(),
            "results": [row.asDict() for row in result_docs]
        })

    return results

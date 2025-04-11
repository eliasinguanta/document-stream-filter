from flask import Flask, request, jsonify
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode
from pydantic import BaseModel
from typing import List

app = Flask(__name__)

# Initialize Spark session
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

@app.route("/filter", methods=["POST"])
def filter_docs():
    try:
        # Read json data from the request
        data = request.get_json()
        
        # Logging
        print("Received data:", data)

        # validate request
        filter_request = FilterRequest(**data)
        
        # create spark data frame
        docs_rdd = spark.sparkContext.parallelize([doc.dict() for doc in filter_request.documents])
        docs_df = spark.read.json(docs_rdd)


        # apply lower case to all words
        docs_df = docs_df.withColumn("words", 
            explode("words")) \
            .withColumn("words", lower(col("words")))

        results = []

        for query in filter_request.queries:
            
            # exact matching
            filtered = docs_df.filter(col("words") == query.word.lower())
            
            # collect & transform results
            docs_filtered = filtered.groupBy("documentName", "size", "mimeType", "uploadDate") \
                                    .count() \
                                    .drop("count")
            result_docs = docs_filtered.collect()
            
            results.append({
                "query": query.dict(),
                "results": [row.asDict() for row in result_docs]
            })

        return jsonify(results)
    
    except Exception as e:
        # Logging
        print("Error occurred:", str(e))
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400



@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3002)

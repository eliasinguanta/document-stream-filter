from flask import Flask, request, jsonify, make_response
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode
from pydantic import BaseModel
from typing import List
from botocore.exceptions import BotoCoreError, ClientError



from dynamo_api import post_document_to_dynamoDB, get_documents_from_dynamoDB, delete_document_from_dynamoDB, delete_all_documents_from_dynamoDB, get_document_from_dynamoDB, post_random_documents_to_dynamoDB, filter_documents


app = Flask(__name__)

class Query(BaseModel):
    queryId: int
    word: str
    metric: str
    distance: int

class FilterRequest(BaseModel):
    queries: List[Query]

@app.route("/filter", methods=["POST"])
def filter_docs():
    try:
        data = request.get_json()
        filter_request = FilterRequest(**data)
        filtered_documents = filter_documents(filter_request.queries)
        
        return jsonify(filtered_documents)

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error occurred:", str(e))
        return make_response('', 500)

# Upload a document to DynamoDB
# The newly created document object is returned
@app.route('/files/', methods=['POST'])
def post_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    try:
        doc = post_document_to_dynamoDB(file)
        return jsonify(doc)
    
    except (BotoCoreError, ClientError, Exception) as e:
        print(f"Error: {e}")
        return make_response('', 500)

# Get all documents from DynamoDB
# Returns a list of dictionaries with the metadata and words of the documents
@app.route('/files/', methods=['GET'])
def get_documents():
    try:
        return jsonify(get_documents_from_dynamoDB()), 200

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error reading metadata from DynamoDB:", e)
        return make_response('', 500)

# Delete a document from DynamoDB
# The document is deleted by its name
@app.route('/files/<filename>', methods=['DELETE'])
def delete_document(filename):
    if not filename:
        print("No filename given")
        return jsonify({"error": "No filename provided"}), 400

    try:
        delete_document_from_dynamoDB(filename)
        return make_response('', 200)

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error deleting metadata from DynamoDB:", e)
        return make_response('', 500)

# Delete all documents from DynamoDB
# Only status code is returned
@app.route('/files/', methods=['DELETE'])
def delete_all_document():
    try:
        delete_all_documents_from_dynamoDB()
        return make_response('', 200)

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error deleting all documents from DynamoDB:", e)
        return make_response('', 500)

# Get a single document from DynamoDB
@app.route('/files/<filename>', methods=['GET'])
def get_document(filename):
    if not filename:
        print("No documentName provided")
        return make_response('', 200)

    try:

        file = get_document_from_dynamoDB(filename)
        response = make_response(file, 200)
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}.txt"'
        response.headers["Content-Type"] = "text/plain"
        return response

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error reading metadata from DynamoDB:", e)
        return make_response('', 500)

# Uplload multiple random generated documents to DynamoDB
# The documents are generated on server-side
# The newly created document objects are returned
@app.route("/randomFiles", methods=["POST"])
def post_random_documents():
    try:
        uploaded_docs = post_random_documents_to_dynamoDB(200)
        return jsonify(uploaded_docs, 200)

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error uploading documents:", e)
        return make_response('', 500)


# Health check endpoint
# Dummy function
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3002)

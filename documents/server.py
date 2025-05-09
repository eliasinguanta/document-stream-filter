from flask import Flask, request, jsonify, make_response

from botocore.exceptions import BotoCoreError, ClientError
from dynamo import post_document_to_dynamoDB, get_documents_from_dynamoDB, delete_document_from_dynamoDB, delete_all_documents_from_dynamoDB, get_document_from_dynamoDB, post_random_documents_to_dynamoDB
from dynamo import logger

app = Flask(__name__)

PREAFIX = "/documents"

# Upload a document to DynamoDB
# The newly created document object is returned
@app.route(f'{PREAFIX}', methods=['POST'])
def post_document():
    logger.debug("Received request to upload a file")
    if 'file' not in request.files:
        logger.debug("No file in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    logger.debug(f'File received: {file.filename}')

    try:
        doc = post_document_to_dynamoDB(file)
        logger.debug("post_document_to_dynamoDB(file) called successfully")
        return jsonify(doc)
    
    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f"Error processing file in post_document(): {e}")
        return make_response(f"Error: {str(e)}", 500)

# Get all documents from DynamoDB
# Returns a list of dictionaries with the metadata and words of the documents
@app.route(f'{PREAFIX}', methods=['GET'])
def get_documents():
    logger.debug("Received request to get files documents")
    try:
        return jsonify([doc.dict() for doc in get_documents_from_dynamoDB()]), 200

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f"Error when getting documents: {str(e)}")
        return make_response('', 500)

# Delete a document from DynamoDB
# The document is deleted by its name
@app.route(f'{PREAFIX}/<filename>', methods=['DELETE'])
def delete_document(filename):
    logger.debug("Received request to delete a file documents")
    if not filename:
        logger.debug("No filename given")
        return jsonify({"error": "No filename provided"}), 400

    try:
        delete_document_from_dynamoDB(filename)
        logger.debug(" delete_document_from_dynamoDB(filename) called successfully")
        return make_response('', 200)

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f'Error deleting metadata from DynamoDB: {str(e)}')
        return make_response('', 500)

# Delete all documents from DynamoDB
# Only status code is returned
@app.route(f'{PREAFIX}', methods=['DELETE'])
def delete_all_document():
    logger.debug("Received request to delete all documents")
    try:
        delete_all_documents_from_dynamoDB()
        logger.debug("delete_all_documents_from_dynamoDB() called successfully")
        return make_response('', 200)

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f'Error deleting all documents from DynamoDB: {str(e)}')
        return make_response('', 500)

# Get a single document from DynamoDB
@app.route(f'{PREAFIX}/<filename>', methods=['GET'])
def get_document(filename):
    logger.debug("Received request to get a file from documents")
    if not filename:
        logger.debug("No documentName provided")
        return make_response('No documentName provided', 400)

    try:
        file = get_document_from_dynamoDB(filename)
        logger.debug("get_document_from_dynamoDB(filename) called successfully")

        response = make_response(file, 200)
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}.txt"'
        response.headers["Content-Type"] = "text/plain"
        logger.debug("Response set successfully")
        return response

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f'Error reading file from DynamoDB: {str(e)}')
        return make_response('', 500)

# Uplload multiple random generated documents to DynamoDB
# The documents are generated on server-side
# The newly created document objects are returned
@app.route(f'{PREAFIX}/random', methods=["POST"])
def post_random_documents():
    logger.debug("Received request to upload random files")
    try:
        uploaded_docs = post_random_documents_to_dynamoDB(200)
        logger.debug("post_random_documents_to_dynamoDB(200) called successfully")
        return jsonify(uploaded_docs, 200)

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f"Error uploading random files in post_random_documents(): {str(e)}")
        return make_response('', 500)

# Health check endpoint
# Dummy function
@app.route(f'{PREAFIX}/health', methods=["GET"])
def health_check():
    logger.debug("Received health check request")
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)

import requests
from flask import Flask, request, jsonify, make_response
from email.utils import parsedate_to_datetime
from filter import filter_documents, logger
from utils import Query, Document

DOCUMENT_SERVICE_URL = "http://dsf-documents/documents"
QUERIY_SERVICE_URL = "http://dsf-queries/queries"
PREAFIX = "/filter"

app = Flask(__name__)

@app.route(f"{PREAFIX}", methods=["GET"])
def filter_docs():
    try:
        logger.debug("Received request to filter documents")

        response = requests.get(DOCUMENT_SERVICE_URL)
        response.raise_for_status()
        logger.debug(f"Received response from document service {response.json()}")
        
        documents = []
        for doc in response.json():
            doc['uploadDate'] = parsedate_to_datetime(doc['uploadDate'])
            documents.append(Document(**doc))
        
        response = requests.get(QUERIY_SERVICE_URL)
        response.raise_for_status()
        queries = [Query(**query) for query in response.json()]
        
        logger.debug("Request data parsed successfully")
        filtered_documents = filter_documents(queries, documents)
        logger.debug("Documents filtered successfully")
        return jsonify(filtered_documents)

    except (Exception) as e:
        logger.error(f'Error occurred: {str(e)}')
        return make_response('', 500)

# Health check endpoint
# Dummy function
@app.route(f"{PREAFIX}/health", methods=["GET"])
def health_check():
    logger.debug("Received health check request")
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)

import boto3
import re
import time
import string
import logging
import random
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.types import TypeDeserializer
from utils import Document

app_name = "document-stream-filter"
logger = logging.getLogger(app_name)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(console_handler)


# DynamoDB Client
dynamodb = boto3.client('dynamodb')
DOCUMENT_TABLE = 'dsf-metadata-db'  # Ersetze mit dem tatsächlichen Tabellennamen
MAX_BATCH_SIZE = 25

deserializer = TypeDeserializer()

# Convert DynamoDB item to Python dict
def dynamodb_item_to_dict(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}

# returns the number of documents that are currently stored in the document table 
def count_documents_in_dynamoDB():
    try:
        response = dynamodb.scan(
            TableName=DOCUMENT_TABLE,
            Select='COUNT'
        )
        return response['Count']
    except (BotoCoreError, ClientError, Exception) as e:
        print("Error counting documents in DynamoDB:", e)
        raise e


# The words of the document are stored in a list and the list is uploaded to DynamoDB with metadata
# Returns the new file with its metadata
def post_document_to_dynamoDB(file):
    if not file:
        raise ValueError("No file uploaded")

    try:
        # We allow the post method only if less then 1000 documents are stored
        if count_documents_in_dynamoDB() >= 1000:
            return []

        # transform the file content into a list of words
        file_content = file.read().decode('utf-8')
        words = re.findall(r'\b\w+\b', file_content)

        # create the file object containing the metadata and words
        file_metadata = {
            'documentName': {'S': file.filename},
            'size': {'N': str(len(file_content))},
            'mimeType': {'S': file.content_type},
            'uploadDate': {'S': datetime.utcnow().isoformat()},
            'words': {'L': [{'S': word} for word in words]}
        }

        # Upload the file object to DynamoDB
        dynamodb.put_item(**{'TableName': DOCUMENT_TABLE,'Item': file_metadata})

        return dynamodb_item_to_dict(file_metadata)

    except (BotoCoreError, ClientError, Exception) as e:
        print(f"Error processing file: {e}")
        raise e
    
# Get all documents from DynamoDB
# Returns a list of dictionaries with the metadata and words of the documents
def get_documents_from_dynamoDB() -> list[Document]:
    try:
        # get request
        response = dynamodb.scan( TableName=DOCUMENT_TABLE )
        logger.debug("Received response from DynamoDB")

        # transform the response into a list of dictionaries
        documents = [Document(**dynamodb_item_to_dict(document)) for document in response.get('Items', [])]
        logger.debug("transform the response into a list of dictionaries")

        return documents

    except (BotoCoreError, ClientError, Exception) as e:
        logger.debug(f'Error reading file from DynamoDB: {e}')
        raise e 

# Delete a document from DynamoDB
# The document is deleted by its name
def delete_document_from_dynamoDB(filename):
    try:
        dynamodb.delete_item( TableName=DOCUMENT_TABLE, Key={'documentName': {'S': filename}})

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error delete file from DynamoDB:", e)
        raise e 

# Delete all documents from DynamoDB
# The documents are deleted in batches of 25
# The function first gets all documents from DynamoDB and then deletes them in batches
def delete_all_documents_from_dynamoDB():
    try:
        # Get all documents
        items: list[Document] = get_documents_from_dynamoDB()
        
        if not items:
            logger.debug("No documents to delete")
            return

        logger.debug(f"delete {len(items)} documents")
        
        # delete in batches of 25
        for i in range(0, len(items), MAX_BATCH_SIZE):
            batch = items[i:i + MAX_BATCH_SIZE]
            logger.debug(f"process Batch {i // MAX_BATCH_SIZE + 1} with {len(batch)} documents.")
            
            request_items = {
                DOCUMENT_TABLE: [
                    {"DeleteRequest": {"Key": {"documentName": {"S": item.documentName}}}} 
                    for item in batch
                ]
            }
            
            logger.debug(f"send batch to dynamoDB: {request_items}")
            
            # Send batch-request
            response = dynamodb.batch_write_item(RequestItems=request_items)
            
            logger.debug(f"response from dynamoDB for Batch {i // MAX_BATCH_SIZE + 1}: {response}")

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error(f"Error for deleting all documents: {e}")
        raise e


# Get a document from DynamoDB
def get_document_from_dynamoDB(filename):
    try:
        
        # get the document object from DynamoDB
        document = dynamodb.get_item(TableName=DOCUMENT_TABLE, Key={'documentName': {'S': filename}}).get('Item')
        
        # transform from dynamoDB object to a list of words
        words = [w['S'] for w in document.get('words', {}).get('L', [])]
        
        # transform the list of words into a string
        return ' '.join(words)

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error reading document from DynamoDB:", e)
        raise e

# Generate a random document with random words
# The document is already in dynamoDB syntax returned
def generate_random_document(index):
    
    # Generate a list of random words
    random_words = [
        ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        for _ in range(100)
    ]

    # Create a document name and file content
    document_name = f"random-{index}-{int(time.time())}.txt"
    file_content = ' '.join(random_words)

    # Create the dynamoDB object
    return {
        'documentName': {'S': document_name},
        'size': {'N': str(len(file_content))},
        'mimeType': {'S': 'text/plain'},
        'uploadDate': {'S': datetime.utcnow().isoformat()},
        'words': {'L': [{'S': word} for word in random_words]}
    }

# Post random documents to DynamoDB
# The documents are generated with random words
# The documents are uploaded in batches of 25
# The function returns the list of new documents
# This function is used for testing purposes

def post_random_documents_to_dynamoDB(count=200):
    try:
        # Check if the document count exceeds 1000
        if count_documents_in_dynamoDB() >= 1000:
            logger.debug("Document count exceeds 1000, returning empty list.")
            return []

        logger.debug(f"Generating {count} random documents.")
        
        # Generate a list of random documents
        documents = [generate_random_document(i) for i in range(count)]
        logger.debug(f"Generated {len(documents)} documents.")
        
        # Upload the documents in batches of 25
        for i in range(0, len(documents), MAX_BATCH_SIZE):
            batch = documents[i:i + MAX_BATCH_SIZE]
            logger.debug(f"Processing batch {i // MAX_BATCH_SIZE + 1} with {len(batch)} documents.")
            
            request_items = {
                DOCUMENT_TABLE: [{'PutRequest': {'Item': doc}} for doc in batch]
            }
            
            logger.debug(f"Sending batch to DynamoDB: {request_items}")
            
            # Upload the batch to DynamoDB
            response = dynamodb.batch_write_item(RequestItems=request_items)
            logger.debug(f"Response from DynamoDB for batch {i // MAX_BATCH_SIZE + 1}: {response}")

        # Transform the documents into a list of dictionaries and return them
        transformed_documents = [dynamodb_item_to_dict(document) for document in documents]
        logger.debug(f"Transformed {len(transformed_documents)} documents into dictionaries.")
        
        return transformed_documents

    except (BotoCoreError, ClientError, Exception) as e:
        logger.error("Error uploading documents: %s", e)
        return e



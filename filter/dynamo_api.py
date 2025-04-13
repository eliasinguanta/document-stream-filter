# file_handler.py
import json
import boto3
import re
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.types import TypeDeserializer
import random
import string
import time

import asyncio
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.conditions import Key
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode
from pydantic import BaseModel


# DynamoDB Client
dynamodb = boto3.client('dynamodb')
DOCUMENT_TABLE = 'dsf-metadata-db'  # Ersetze mit dem tatsächlichen Tabellennamen
MAX_BATCH_SIZE = 25

# Initialize Spark session
spark = SparkSession.builder \
    .appName("document-stream-filter") \
    .getOrCreate()

deserializer = TypeDeserializer()

# Convert DynamoDB item to Python dict
def dynamodb_item_to_dict(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}

# The words of the document are stored in a list and the list is uploaded to DynamoDB with metadata
# Returns the new file with its metadata
def post_document_to_dynamoDB(file):
    if not file:
        raise ValueError("No file uploaded")

    try:
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
def get_documents_from_dynamoDB():
    try:
        # get request
        response = dynamodb.scan( TableName=DOCUMENT_TABLE )
        
        # transform the response into a list of dictionaries
        documents = [ dynamodb_item_to_dict(document) for document in response.get('Items', [])]
        return documents

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error reading file from DynamoDB:", e)
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
        # Get all items from the table
        items = get_documents_from_dynamoDB()
        if not items:
            return

        # Delete items in batches of 25
        for i in range(0, len(items), MAX_BATCH_SIZE):
            batch = items[i:i + MAX_BATCH_SIZE]
            request_items = { DOCUMENT_TABLE: [{"DeleteRequest": { "Key": { "documentName": { "S": item["documentName"] }}}} for item in batch ]}
            dynamodb.batch_write_item(RequestItems = request_items)

    except (BotoCoreError, ClientError, Exception) as e:
        print(" Error for deleting all documents", e)
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
    document_name = f"random-doc-debug-{index}-{int(time.time() * 1000)}.txt"
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
        
        # Generate a list of random documents
        documents = [generate_random_document(i) for i in range(count)]

        # Upload the documents in batches of 25
        for i in range(0, len(documents), MAX_BATCH_SIZE):
            batch = documents[i:i + MAX_BATCH_SIZE]
            request_items = { DOCUMENT_TABLE: [{'PutRequest': {'Item': doc}} for doc in batch]}
            dynamodb.batch_write_item(RequestItems=request_items)

        # Transform the documents into a list of dictionaries and return them
        return [dynamodb_item_to_dict(document) for document in documents]

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error uploading documents:", e)
        return e
    
def filter_documents(queries):
    try:

        # Dokumente laden – Liste von dicts
        documents = get_documents_from_dynamoDB()

        # Direkt Spark DataFrame erstellen
        docs_df = spark.createDataFrame(documents)

        # Worte aufsplitten und klein schreiben
        docs_df = docs_df.withColumn("words", explode(col("words"))) \
                         .withColumn("words", lower(col("words")))

        results = []

        for query in queries:
            filtered = docs_df.filter(col("words") == query.word.lower())

            docs_filtered = filtered.groupBy("documentName", "size", "mimeType", "uploadDate") \
                                    .count() \
                                    .drop("count")

            result_docs = docs_filtered.collect()

            results.append({
                "query": query.dict(),
                "results": [row.asDict() for row in result_docs]
            })

        return results

    except (BotoCoreError, ClientError, Exception) as e:
        print("Error occurred:", str(e))
        raise e
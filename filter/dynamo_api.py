# file_handler.py
import boto3
import re
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError
from boto3.dynamodb.types import TypeDeserializer
import random
import string
import time

from botocore.exceptions import BotoCoreError, ClientError
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode, levenshtein, udf, lit, length
import logging
from pyspark.sql.types import IntegerType

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
        
        if count_documents_in_dynamoDB() >= 1000:
            return []
        
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

# Initialize Spark session
spark = SparkSession.builder \
    .appName(app_name) \
    .getOrCreate()

@udf(returnType=IntegerType())
def hamming_distance(a, b):
    dist = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            dist += 1
    return dist

def filter_documents(queries):
    try:
        logger.debug("Fetching documents from DynamoDB...")
        documents = get_documents_from_dynamoDB()
        logger.debug(f"Fetched {len(documents)} documents.")

        logger.debug("Creating Spark DataFrame...")
        docs_df = spark.createDataFrame(documents)
        logger.debug("DataFrame schema:")
        docs_df.printSchema()

        logger.debug("Exploding and lowering words column...")
        docs_df = docs_df.withColumn("words", explode(col("words"))) \
                         .withColumn("words", lower(col("words")))

        results = []

        for query in queries:
            logger.debug(f"Processing query: {query.word}")
            
            if query.metric.lower() == "exact":
                filtered = docs_df.filter(col("words") == query.word.lower())
            elif query.metric.lower() == "edit":
                filtered = docs_df.filter(levenshtein(col("words"), lit(query.word.lower())) <= lit(query.distance))
            elif query.metric.lower() == "hamming":
                filtered = docs_df \
                    .filter(length(col("words")) == len(query.word)) \
                    .filter(hamming_distance(col("words"), lit(query.word.lower())) <= lit(query.distance))
            else:
                raise ValueError(f"Invalid metric: {query.metric}")
                    
            logger.debug("Filtered rows:")

            filtered_documents = filtered.groupBy("documentName", "size", "mimeType", "uploadDate") \
                .count() \
                .drop("count") \
                .collect()
           
            logger.debug(f"Found {len(filtered_documents)} results for query: {query.word}")

            results.append({
                "query": query.dict(),
                "results": [row.asDict() for row in filtered_documents]
            })

        return results

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise e


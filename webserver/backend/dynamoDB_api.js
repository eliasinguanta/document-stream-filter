import { DynamoDBClient, PutItemCommand, ScanCommand, DeleteItemCommand, GetItemCommand, BatchWriteItemCommand } from '@aws-sdk/client-dynamodb'; // Importieren des DynamoDB Clients und der PutItemCommand
import { unmarshall } from "@aws-sdk/util-dynamodb"

const client = new DynamoDBClient({});
const DOCUMENT_TABLE = 'dsf-metadata-db';

// Middleware for uploading file to DynamoDB
export async function postDocument(req, res, next) {

  // Check if client sent a file
  if (!req.file) {
    console.error("No file uploaded");
    return res.sendStatus(500);
  }

  try {

    // Read file content
    const fileContent = req.file.buffer.toString("utf-8");

    // Transform file to list of words
    const words = fileContent.match(/\b\w+\b/g) || []; // RegEx extrahiert Wörter

    // Filter metadata from file
    const fileMetadata = {
      documentName: { S: req.file.originalname },
      size: { N: req.file.size.toString() },
      mimeType: { S: req.file.mimetype },
      uploadDate: { S: new Date().toISOString() },
      words: { L: words.map(word => ({ S: word })) }
    };


    // Upload metadata to DynamoDB
    await client.send(new PutItemCommand({ TableName: DOCUMENT_TABLE, Item: fileMetadata }));
    const data = await client.send(
      new ScanCommand({
        TableName: DOCUMENT_TABLE,
        ProjectionExpression: "documentName, size",
        FilterExpression: "documentName = :documentName",
        ExpressionAttributeValues: {
          ":documentName": { S: req.file.originalname }
        }
      })
    );
    

    // transfrom the data to a more readable format
    res.locals.metadata = data.Items.map(item => unmarshall(item))[0];

    next();
  } catch (err) {
    console.error("Error processing file:", err);
    return res.sendStatus(500);
  }
}

// Middleware for getting a list of all filenames and sizes
export async function getDocumentNameAndSize(req, res, next) {
  try {

    // Scan table
    const data = await client.send(new ScanCommand({ TableName: DOCUMENT_TABLE, ProjectionExpression: "documentName, size" }));

    // Format data for response
    res.locals.metadata = data.Items.map(item => unmarshall(item));

    next();
  } catch (err) {
    console.error("Error reading metadata from DynamoDB:", err);
    res.sendStatus(500);
  }
}

// Middleware for getting all documents
export async function getDocuments(req, res, next) {
  try {

    // Scan table
    const data = await client.send(new ScanCommand({ TableName: DOCUMENT_TABLE}));

    // Format data for response
    res.locals.documents = data.Items.map(item => unmarshall(item));

    next();
  } catch (err) {
    console.error("Error reading metadata from DynamoDB:", err);
    res.sendStatus(500);
  }
}

// Middleware for deleting a file from DynamoDB
export async function deleteDocument(req, res, next) {

  // Check if a filename is provided
  if (!req.params.filename) {
    console.error("no filename given");
    return res.sendStatus(400);
  }

  try {
    // delete metadata from DynamoDB
    await client.send(new DeleteItemCommand({ TableName: DOCUMENT_TABLE, Key: { documentName: { S: req.params.filename } } }));

    next();
  } catch (error) {
    console.error("Error deleting metadata from DynamoDB:", error);
    return res.sendStatus(500);
  }
}

export async function deleteAllDocuments(req, res, next) {
  try {
    const data = await client.send(new ScanCommand({ TableName: DOCUMENT_TABLE }));

    if (!data.Items || data.Items.length === 0) {
      return res.status(200).json({ message: "No documents to delete." });
    }

    const items = data.Items;
    const batchSize = 25;

    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);

      const requestItems = {};
      requestItems[DOCUMENT_TABLE] = batch.map((item) => ({
        DeleteRequest: {
          Key: {
            documentName: item.documentName,
          },
        },
      }));

      await client.send(
        new BatchWriteItemCommand({
          RequestItems: requestItems,
        })
      );
    }

    next();
  } catch (error) {
    console.error("Error while deleting all documents:", error);
    res.sendStatus(500);
  }
}

// Middleware for getting a file from DynamoDB
export async function getDocument(req, res) {

  // Check if a filename is provided
  if (!req.params.filename) {
    console.error("No documentName provided");
    return res.sendStatus(400);
  }

  try {

    // Get file from DynamoDB
    const data = await client.send(new GetItemCommand({ TableName: DOCUMENT_TABLE, Key: { documentName: { S: req.params.filename } } }));

    // Check if file exists
    if (!data.Item) {
      console.error("File not found in DynamoDB");
      return res.sendStatus(404);
    }

    // transform the data
    const words = data.Item.words ? data.Item.words.L.map(w => w.S) : [];
    const fileContent = words.join(" "); // Wörter mit Leerzeichen verbinden

    // send the textfile
    res.setHeader("Content-Disposition", `attachment; filename="${req.params.filename}.txt"`);
    res.setHeader("Content-Type", "text/plain");
    res.send(fileContent);

  } catch (err) {
    console.error("Error reading metadata from DynamoDB:", err);
    return res.sendStatus(500);
  }
}

function generateRandomDocument(index) {
  const randomWords = Array.from({ length: 100 }, () =>
    Math.random().toString(36).substring(2, 8)
  );

  const documentName = `random-doc-${index}-${Date.now()}.txt`;

  return {
    documentName: { S: documentName },
    size: { N: (randomWords.join(" ").length).toString() },
    mimeType: { S: "text/plain" },
    uploadDate: { S: new Date().toISOString() },
    words: { L: randomWords.map((word) => ({ S: word })) },
  };
}

export async function postRandomDocuments(req, res, next) {
  const n = parseInt(req.query.count) || 200;
  const uploadedDocs = [];

  const documents = Array.from({ length: n }, (_, i) => generateRandomDocument(i));

  // In Batches von 25 teilen
  const batchSize = 25;
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);

    const requestItems = {};
    requestItems[DOCUMENT_TABLE] = batch.map((doc) => ({
      PutRequest: {
        Item: doc,
      },
    }));

    try {
      await client.send(
        new BatchWriteItemCommand({
          RequestItems: requestItems,
        })
      );

      uploadedDocs.push(
        ...batch.map((doc) => ({
          documentName: doc.documentName.S,
          size: doc.size.N,
        }))
      );


    } catch (err) {
      console.error("Error uploading batch:", err);
      return res.status(500).json({ error: "Error uploading documents in batch" });
    }
  }
  res.locals.generatedDocuments = uploadedDocs;
  next();
}



const QUERY_TABLE = 'dsf-queries-db';


// Every query has a unique id, which is the maximum id + 1
// To upload a new query, we need to know the maximum id
async function getMaxQueryId(){
  // Scan table for all queryIds
  const data = await client.send( new ScanCommand({ TableName: QUERY_TABLE, ProjectionExpression: "queryId" }));

  // If no items are found we start at id 0
  if (!data.Items || data.Items.length === 0) return 0

  // If items are found we transfrom the data to a simple array of queryIds
  const queryIds = data.Items.map(item => unmarshall(item).queryId).map(id => parseInt(id))

  // Get the maximum queryId
  const maxQueryId = queryIds.reduce((max, current) => { return current > max ? current : max;}, 0);
  return maxQueryId;
}

// Next queryId is the maximum queryId + 1
let nextId = await getMaxQueryId() + 1;

// Middleware for uploading a query to DynamoDB
// A Query consists of a word, a metric and a distance
export async function postQueries(req, res, next) {

  // Check if sent query is complete
  const { word, metric, distance } = req.body
  if (!word || !metric || distance == null)  return res.sendStatus(400);
  

  try {
    // Create query object in database format
    const query = {
      queryId: { N: String(nextId++) }, // key
      word: { S: word }, // query word
      metric: { S: metric }, // query metric
      distance: { N: String(distance) }, // query distance
    };

    // Upload query to DynamoDB
    await client.send(new PutItemCommand({ TableName: QUERY_TABLE, Item: query }));

    // Store the query also in res.locals for the next middleware
    res.locals.new_query = unmarshall(query);

    next();
  } catch (err) {
    console.error("Error processing query upload:", err);
    return res.sendStatus(500);
  }
}

// Middleware for getting all queries from DynamoDB
export async function getQueries(req, res, next) {
  try {

    // Scan entire queries-table
    const data = await client.send(new ScanCommand({ TableName: QUERY_TABLE }));

    // Format data for response
    res.locals.queries = data.Items.map(item => unmarshall(item));

    next();
  } catch (err) {
    console.error("Error reading queries from DynamoDB:", err);
    res.sendStatus(500);
  }
}

// Middleware for deleting a file from DynamoDB
export async function deleteQueries(req, res, next) {

  // Check if a filename is provided
  if (!req.params.id) {
    console.error("no id given");
    return res.sendStatus(400);
  }

  try {
    // Delete metadata from DynamoDB
    await client.send(new DeleteItemCommand({ TableName: QUERY_TABLE, Key: { queryId: { N: req.params.id } } }));

    next();
  } catch (error) {
    console.error("Error deleting metadata from DynamoDB:", error);
    return res.sendStatus(500);
  }
}
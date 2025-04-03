import { DynamoDBClient, PutItemCommand, ScanCommand, DeleteItemCommand, GetItemCommand } from '@aws-sdk/client-dynamodb'; // Importieren des DynamoDB Clients und der PutItemCommand
import { unmarshall } from "@aws-sdk/util-dynamodb"

const client = new DynamoDBClient({});
const TABLE_NAME = 'dsf-metadata-db';

// Middleware for uploading file to DynamoDB
export async function postDocument(req, res, next) {

  // Check if client sent a file
  if (!req.file) {
    console.error("No file uploaded");
    return res.sendStatus(500);
  }

  try {

    // Falls du den Inhalt der Datei verarbeiten musst, z.B. in Text umwandeln
    const fileContent = req.file.buffer.toString("utf-8");

    // transform file to list of words
    const words = fileContent.match(/\b\w+\b/g) || []; // RegEx extrahiert Wörter

    // Filter metadata from file
    const fileMetadata = {
      documentName: { S: req.file.originalname }, // Partition Key
      size: { N: req.file.size.toString() },      // Document size in bytes
      mimeType: { S: req.file.mimetype },
      uploadDate: { S: new Date().toISOString() },
      words: { L: words.map(word => ({ S: word })) } // Begrenzung auf 1000 Wörter für DynamoDB-Größe
    };

    // Create upload command
    const command = new PutItemCommand({
      TableName: TABLE_NAME,
      Item: fileMetadata,
    });

    // Upload metadata to DynamoDB
    await client.send(new PutItemCommand({ TableName: TABLE_NAME, Item: fileMetadata }));

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
    const data = await client.send(new ScanCommand({ TableName: TABLE_NAME, ProjectionExpression: "documentName, size" }));

    // Format data for response
    res.locals.metadata = data.Items.map(item => unmarshall(item));

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
    await client.send(new DeleteItemCommand({ TableName: TABLE_NAME, Key: { documentName: { S: req.params.filename } } }));

    next();
  } catch (error) {
    console.error("Error deleting metadata from DynamoDB:", error);
    return res.sendStatus(500);
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
    const data = await client.send(new GetItemCommand({ TableName: TABLE_NAME, Key: { documentName: { S: req.params.filename } } }));

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
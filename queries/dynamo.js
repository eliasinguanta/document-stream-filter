import { DynamoDBClient, PutItemCommand, ScanCommand, DeleteItemCommand } from '@aws-sdk/client-dynamodb'; // Importieren des DynamoDB Clients und der PutItemCommand
import { unmarshall } from "@aws-sdk/util-dynamodb"

const client = new DynamoDBClient({});
const QUERY_TABLE = 'dsf-queries-db';


// Every query has a unique id, which is the maximum id + 1
// To upload a new query we need to know the maximum id
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
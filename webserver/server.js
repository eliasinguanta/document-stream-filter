import express from "express";
import fetch from 'node-fetch';

import {getWebsiteFromS3} from "./backend/s3_api.js";
import {transfromInput} from "./backend/utils.js";
import {postDocument, getDocumentNameAndSize, deleteDocument, getDocument, getDocuments, postQueries, getQueries, deleteQueries } from "./backend/dynamoDB_api.js";
const app = express();
const PORT = 3000;
const FILTER_URL = "a06d53fda98cc45b68ee43b43e8fc0ca-138658565.eu-north-1.elb.amazonaws.com";

// health check
// basically a ping to check if the server is running
// For AWS ELB a health check endpoint is required (but i also just could use the "/" endpoint)
app.get("/health", (req, res) => {
  res.sendStatus(200);
});

// delete a single file and its metadata
app.delete("/files/:filename", deleteDocument, (req, res) => {
  res.sendStatus(200);
});

// upload a file and its metadata
app.post("/files", transfromInput, postDocument, (req, res) => {
  res.status(200).json(res.locals.metadata);
});

// get a list of all files
app.get("/files", getDocumentNameAndSize, (req, res) => {
    console.log(res.locals.metadata);
    res.status(200).json({ files: res.locals.metadata });
});

// get a single file
app.get("/files/:filename", getDocument);

// get all queries
app.get('/queries', getQueries, (req, res) => {
  res.json(res.locals.queries)
})


// post a single query
app.post('/queries', express.json(),postQueries, (req, res) => {
  res.json(res.locals.new_query);
})

// delete a single query
app.delete('/queries/:id', deleteQueries, (req, res) => {
  res.sendStatus(200);
})


app.get('/filter', getDocuments, getQueries, async (req, res) => {
  const documents = res.locals.documents;
  const queries = res.locals.queries;

  console.log(documents);
  console.log(queries);

  try {
    const response = await fetch('http://'+FILTER_URL+'/filter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        documents: documents,
        queries: queries,
      }),
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Fehler bei der HTTP-Anfrage:', error);
    res.status(500).json({ error: 'Serverfehler' });
  }
});



// get the website
app.get("*", getWebsiteFromS3, async (req, res) => {
  res.end();
});


//start http server
app.listen(PORT, () => {
  console.log(`server runs on http://localhost:${PORT}`);
});
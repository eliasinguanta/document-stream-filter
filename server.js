import express from "express";

import {getWebsiteFromS3} from "./backend/s3_api.js";
import {transfromInput} from "./backend/utils.js";
import {postDocument, getDocumentNameAndSize, deleteDocument, getDocument, postQueries, getQueries, deleteQueries } from "./backend/dynamoDB_api.js";
const app = express();
const PORT = 3000;

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

app.get('/filter', (req, res) => {
  res.json({
    results: [
      {
        query: { word: "hallo", metric: "edit", distanz: 2 },
        results: [
          { name: "Dokument1.pdf", size: "1.2 MB" },
          { name: "Dokument4.pdf", size: "450 KB" }
        ]
      },
      {
        query: { word: "meeting", metric: "edit", distanz: 3 },
        results: [
          { name: "Dokument4.pdf", size: "450 KB" }
        ]
      },
      {
        query: { word: "projekt", metric: "edit", distanz: 1 },
        results: [
          { name: "Dokument2.pdf", size: "850 KB" },
          { name: "Dokument3.pdf", size: "3.1 MB" }
        ]
      }
    ]
  });
})


// get the website
app.get("*", getWebsiteFromS3, async (req, res) => {
  res.end();
});


//start http server
app.listen(PORT, () => {
  console.log(`server runs on http://localhost:${PORT}`);
});
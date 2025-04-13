import express from "express";
import fetch from 'node-fetch';

import {getWebsiteFromS3} from "./backend/s3_api.js";
import { createProxyMiddleware } from "http-proxy-middleware";

import {postQueries, getQueries, deleteQueries } from "./backend/dynamoDB_api.js";
const app = express();
const PORT = 3000;
const FORWARD_URL = "a06d53fda98cc45b68ee43b43e8fc0ca-138658565.eu-north-1.elb.amazonaws.com"

// Create a proxy for endpoint /files
const proxy_for_files = createProxyMiddleware({
  target: `http://${FORWARD_URL}`,
  changeOrigin: true,
  pathRewrite: {
    "^/": "/files/"
  }
});

// Middleware for GET and POST requests on /files
// Forward requests to the spark cluster that is our dynamoDB api
app.use("/files", proxy_for_files);


// Create a proxy for endpoint /files
const proxy_for_random_files = createProxyMiddleware({
  target: `http://${FORWARD_URL}`,
  changeOrigin: true,
  pathRewrite: {
    "^/": "/randomFiles"
  }
});

app.use("/randomFiles", proxy_for_random_files);

app.get('/filter', getQueries, async (req, res) => {
  const queries = res.locals.queries;

  console.log(queries);

  try {
    const response = await fetch('http://'+FORWARD_URL+'/filter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({queries: queries,}),
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Fehler bei der HTTP-Anfrage:', error);
    res.status(500).json({ error: 'Serverfehler' });
  }
});

// health check
// basically a ping to check if the server is running
// For AWS ELB a health check endpoint is required (but i also just could use the "/" endpoint)
app.get("/health", (req, res) => {
  res.sendStatus(200);
});

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

// get the website
app.get("*", getWebsiteFromS3, async (req, res) => {
  res.end();
});


//start http server
app.listen(PORT, () => {
  console.log(`server runs on http://localhost:${PORT}`);
});
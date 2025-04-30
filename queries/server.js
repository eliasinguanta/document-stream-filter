import express from "express";

import {postQueries, getQueries, deleteQueries } from "./dynamo.js"; //queries/dynamo.js
const app = express();
const PORT = 3003;

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

//start http server
app.listen(PORT, () => {
    console.log(`server runs on http://localhost:${PORT}`);
  });
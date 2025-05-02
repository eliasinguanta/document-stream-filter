import express from "express";

import {postQueries, getQueries, deleteQueries } from "./dynamo.js"; //queries/dynamo.js
const app = express();
const PORT = 80;
const PREFIX = "/queries"
app.get(PREFIX + "/health", (req, res) => {
    res.sendStatus(200);
  });

// get all queries
app.get(PREFIX, getQueries, (req, res) => {
  res.json(res.locals.queries)
})

// post a single query
app.post(PREFIX, express.json(),postQueries, (req, res) => {
  res.json(res.locals.new_query);
})

// delete a single query
app.delete(PREFIX + '/:id', deleteQueries, (req, res) => {
  res.sendStatus(200);
})

//start http server
app.listen(PORT, () => {
    console.log(`server runs on http://localhost:${PORT}`);
  });
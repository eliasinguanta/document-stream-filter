import express from "express";

import {getWebsiteFromS3} from "./s3.js";

const app = express();
const PORT = 80;
const PREAFIX = "/website";
// health check endpoint
// basically a ping to check if the server is running
// For AWS ELB a health check endpoint is required (but i also just could use the "/" endpoint)
app.get(PREAFIX+"/health", (req, res) => {
  res.sendStatus(200);
});

// get the website
app.use(PREAFIX, getWebsiteFromS3);

//start http server
app.listen(PORT, () => {
  console.log(`server runs on http://localhost:${PORT}${PREAFIX}`);
});
import express from "express";

import {getWebsiteFromS3} from "./backend/s3_api.js";

const app = express();
const PORT = 80;
const PREAFIX = "/website";

// health check
// basically a ping to check if the server is running
// For AWS ELB a health check endpoint is required (but i also just could use the "/" endpoint)
app.get(PREAFIX+"/health", (req, res) => {
  res.sendStatus(200);
});

// get the website
app.get(PREAFIX, getWebsiteFromS3, async (req, res) => {
  res.end();
});

//start http server
app.listen(PORT, () => {
  console.log(`server runs on http://localhost:${PORT}`);
});
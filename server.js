import express from "express";
import https from 'https';
import fs from "fs";

import {getWebsiteFromS3} from "./backend/s3_api.js";
import {transfromInput} from "./backend/utils.js";
import {postDocument, getDocumentNameAndSize, deleteDocument, getDocument } from "./backend/dynamoDB_api.js";
const app = express();
const PORT = 3000;

// delete a single file and its metadata
app.delete("/files/:filename", deleteDocument, (req, res) => {
  res.sendStatus(200);
});

// upload a file and its metadata
app.post("/files", transfromInput, postDocument, (req, res) => {
  res.sendStatus(200);
});

// get a list of all files
app.get("/files", getDocumentNameAndSize, (req, res) => {
    console.log(res.locals.metadata);
    res.status(200).json({ files: res.locals.metadata });
  
});

// get a single file
app.get("/files/:filename", getDocument);

app.get("/health", (req, res) => {
  res.sendStatus(200);
});

// get the website
app.get("*", getWebsiteFromS3, async (req, res) => {
  res.end();
});

// Lade das Zertifikat und den privaten Schlüssel
const privateKey = fs.readFileSync('ssl/server.key', 'utf8');
const certificate = fs.readFileSync('ssl/server.crt', 'utf8');

// Erstelle die HTTPS-Serverinstanz
const credentials = { key: privateKey, cert: certificate };

https.createServer(credentials, app).listen(PORT, async () => {
  console.log(`server runs on https://localhost:${PORT}`);
});
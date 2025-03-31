import express from "express";
import fs from "fs";
import path from "path";
import { S3Client, PutObjectCommand, GetObjectCommand, NoSuchKey, S3ServiceException } from "@aws-sdk/client-s3";
import { fileURLToPath } from "url";


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// use AWS CLI login info
const s3Client = new S3Client({});

// define bucket name
const BUCKET_NAME = "document-stream-filter-bucket";

const app = express();
const PORT = 3000;

// convert stream to string
const streamToString = (stream) => {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    stream.on("error", reject);
  });
};

// determine the content type based on the file extension
const getContentType = (file) => {
  const extname = path.extname(file).toLowerCase();
  return {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
  }[extname] || "application/octet-stream";
};

// download file from s3 bucket
export const getFileFromS3 = async ({ bucketName, key }) => {

  try {
    // request the object from S3
    const response = await s3Client.send(
      new GetObjectCommand({
        Bucket: bucketName,
        Key: key,
      })
    );

    // convert the stream to string
    const str = await streamToString(response.Body);
    return str;
  }
  // handle errors
  catch (caught) {
    if (caught instanceof NoSuchKey) {
      console.error(
        `Error from S3 while getting object "${key}" from "${bucketName}". No such key exists.`
      );
    } else if (caught instanceof S3ServiceException) {
      console.error(
        `Error from S3 while getting object from ${bucketName}. ${caught.name}: ${caught.message}`
      );
    } else {
      throw caught;
    }
    return null;
  }
};

// start server
app.listen(PORT, async () => {
  console.log(`server runs on http://localhost:${PORT}`);

  //return current website from s3 bucket 
  app.get("*", async (req, res) => {
    const filePath = req.url === "/" ? "index.html" : req.url.substring(1); // remove leading "/"

    try {
      // get the object from s3 bucket
      const res_body = await getFileFromS3({ bucketName: BUCKET_NAME, key: filePath });

      // determine the content type and return the response
      if (res_body) {
        const contentType = getContentType(filePath);
        res.setHeader("Content-Type", contentType);
        res.send(res_body);
      } else { //bad request
        res.status(404).send("file not found");
      }
    } catch (error) { //server error
      console.error("error: ", error);
      res.status(500).send("server error");
    }
  });
});

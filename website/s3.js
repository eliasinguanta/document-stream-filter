import path from "path";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { url } from "inspector";

const myS3Client = new S3Client({});
const BUCKET_NAME = "document-stream-filter-bucket";

const streamToString = (stream) => {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    stream.on("error", reject);
  });
};

const getContentType = (file) => {
  const extname = path.extname(file).toLowerCase();
  return {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
  }[extname] || "application/octet-stream";
};

//downloads the web site files like html, css, js for vue from a aws s3 bucket
export async function getWebsiteFromS3(req, res) {
  const filePath = req.url === "/" ? "index.html" : req.url.substring(1);

  try {
    // request the object from S3
    const response = await myS3Client.send(
      new GetObjectCommand({
        Bucket: BUCKET_NAME,
        Key: filePath,
      })
    );

    // convert the stream to string
    res.setHeader("Content-Type", getContentType(filePath));
    res.send(await streamToString(response.Body));

  } catch (error) { //server error
    console.error("website not found: ", error);
    res.status(500).json({
      req: req.url,
      filePath: filePath,
      error: error.message
  });
  }
}
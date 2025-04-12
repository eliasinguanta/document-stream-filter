
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { streamToString, getContentType } from "./utils.js";

const myS3Client = new S3Client({});
const BUCKET_NAME = "document-stream-filter-bucket";

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
    res.sendStatus(500);
  }
}
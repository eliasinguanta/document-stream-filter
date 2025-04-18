import path from "path";

// transform the input stream to string
export const streamToString = (stream) => {
  return new Promise((resolve, reject) => {
    const chunks = [];
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
    stream.on("error", reject);
  });
};

// get the content type of the file based on its extension
export const getContentType = (file) => {
  const extname = path.extname(file).toLowerCase();
  return {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
  }[extname] || "application/octet-stream";
};

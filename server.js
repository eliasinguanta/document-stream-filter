const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

// static files
app.use(express.static(path.join(__dirname, "dist")));

// fallback
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

app.listen(PORT, () => {
  console.log("server runs on http://localhost:${PORT}");
});

import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import multer from "multer";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);


const DOCUMENT_DIR = path.join(__dirname, "uploads");
const DOCUMENT_METADATA_DIR = path.join(__dirname, "metadata");

// create directories if they do not exist
if (!fs.existsSync(DOCUMENT_DIR)) {
    fs.mkdirSync(DOCUMENT_DIR);
}
if (!fs.existsSync(DOCUMENT_METADATA_DIR)) {
    fs.mkdirSync(DOCUMENT_METADATA_DIR);
}

// multer configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, DOCUMENT_DIR);
    },
    filename: (req, file, cb) => {
        cb(null, file.originalname);
    }
});
const document_storage = multer({ storage });

// Middleware to delete a document from the local filesystem
export function deleteFile(req, res, next) {
    const filePath = path.join(DOCUMENT_DIR, req.params.filename);

    if (!filePath) return res.sendStatus(400);

    fs.unlink(filePath, (err) => {
        if (err) return res.sendStatus(500);
        next();
    });
}

// Middleware to delete metadata of a document from the local filesystem
export function deleteMetaData(req, res, next) {
    const metadataFilePath = path.join(DOCUMENT_METADATA_DIR, `${req.params.filename}.json`);

    if (!metadataFilePath) return res.sendStatus(400);

    fs.unlink(metadataFilePath, (err) => {
        if (err) return res.sendStatus(500);
        next();
    });
}

// Middleware to store the metadata of a given document in the local filesystem
export function postMetaData(req, res, next) {

    // Check if a file is received from client
    if (!req.file) {
        console.error("No file uploaded");
        return res.sendStatus(500);
    }

    // filter metadata from request
    const fileMetadata = {
        documentName: req.file.originalname,
        size: req.file.size,
        mimeType: req.file.mimetype,
        uploadDate: new Date().toISOString(),
    };

    // Save metadata to a JSON file in local filesystem
    const metadataFilePath = path.join(DOCUMENT_METADATA_DIR, `${req.file.originalname}.json`);
    fs.writeFile(metadataFilePath, JSON.stringify(fileMetadata, null, 2), (err) => {
        if (err) {
            console.error("Error saving metadata:", err);
            return res.sendStatus(500);
        }
        next();
    });
}

// Middleware to store a document in the local filesystem
export function postFile(req, res, next) {
    document_storage.single("file")(req, res, (err) => {
        if (err) {
            console.error("Error uploading file:", err);
            return res.sendStatus(500);
        }
        next();
    });
}

// Middleware to get the metadata of all documents in the local filesystem
export function getMetaData(req, res, next) {
    try {
        const files = fs.readdirSync(DOCUMENT_METADATA_DIR);
        res.locals.metadata = files.map(file => {
            const filePath = path.join(DOCUMENT_METADATA_DIR, file);
            const metaData = fs.readFileSync(filePath, "utf8");
            return JSON.parse(metaData);
        });

        next();
    } catch (err) {
        console.error("Error reading metadata: ", err);
        res.sendStatus(500);
    }
}

// Middleware to get a specific document from the local filesystem
export function getFile(req, res) {
    const filename = req.params.filename;
    const filePath = path.join(DOCUMENT_DIR, filename);

    if (!fs.existsSync(filePath)) {
        console.log("file not found");
        return res.sendStatus(404);
    }

    res.download(filePath, filename, (err) => {
        if (err) {
            console.error("donwload error: ", err);
            res.sendStatus(500);
        }
    });
}

export function storeFileInRequest(req, res, next) {
    const form = new IncomingForm();
    
    form.parse(req, (err, fields, files) => {
        if (err) {
            console.error("Fehler beim Hochladen:", err);
            return res.sendStatus(500); // Fehler beim Hochladen der Datei
        }

        // Datei in req.file speichern
        if (files && files.file) {
            req.file = {
                path: files.file[0].filepath,  // Dateipfad
                filename: files.file[0].originalFilename,  // Original-Dateiname
                mimetype: files.file[0].mimetype,  // Dateityp (z.B. text/plain)
                size: files.file[0].size,  // Dateigröße
            };
            next(); // Wenn alles ok, gehe zum nächsten Schritt
        } else {
            res.sendStatus(400); // Keine Datei hochgeladen
        }
    });
}
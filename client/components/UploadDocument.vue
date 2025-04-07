<template>
  <div class="container mt-5">

    <!-- Table displaying uploaded documents only if there are documents -->
    <div v-if="uploadedDocuments.length > 0">
      <table class="table">
        <thead>
          <tr>
            <th scope="col"></th>
            <th scope="col">Name</th>
            <th scope="col">Size</th>
            <th scope="col"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(doc, index) in uploadedDocuments" :key="index">
            <th scope="row">{{ index + 1 }}</th>
            <td>{{ doc.name }}</td>
            <td>{{ doc.size }} bytes</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="deleteFile(doc.name)"> Delete </button>
              <button class="btn btn-success btn-sm ms-2" @click="downloadFile(doc.name)"> Download </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- File upload form -->
    <div class="mb-3">
      <input type="file" class="form-control" @change="setUploadDocument" ref="fileInput" />
    </div>

    <!-- Button to upload the document -->
    <button class="btn btn-primary" @click="uploadDocument">Upload Document</button>

  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";

// Reaktive Variablen
const selectedFile = ref(null);
const uploadedDocuments = ref([]);

const setUploadDocument = (event) => {
  selectedFile.value = event.target.files[0];
};

// Funktion zum Hochladen des Dokuments
const uploadDocument = async () => {

  if (!selectedFile.value) {
    alert("Please select a file to upload.");
    return;
  }
  if (selectedFile.value.type !== "text/plain") {
    alert("Please select a text file");
    selectedFile.value = null;
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const response = await fetch("/files", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();


      uploadedDocuments.value.push({
        name: data.documentName,
        size: data.size,
      });

    } else {
      alert("Upload failed: " + response.status);
    }
  } catch (error) {
    alert("An error occurred while uploading the file: " + error.message);
  }

  // Zurücksetzen
  selectedFile.value = null;
};

// Funktion zum Abrufen der hochgeladenen Dateien
const fetchFiles = async () => {
  try {
    const response = await fetch("/files");
    const data = await response.json();
    uploadedDocuments.value = data.files.map((file) => ({
      name: file.documentName,
      size: file.size,
    }));
  } catch (error) {
    alert("Error fetching files: " + error.message);
  }
};

// Funktion zum Löschen einer Datei
const deleteFile = async (filename) => {
  try {
    const response = await fetch(`/files/${filename}`, {
      method: "DELETE",
    });

    if (response.ok) {
      console.log(`File ${filename} deleted successfully`);
      fetchFiles();  // Nach dem Löschen die Dateien erneut abrufen
    } else {
      alert("Error deleting file.");
    }
  } catch (error) {
    console.error("Error deleting file:", error);
    alert("An error occurred while deleting the file.");
  }
};

// Funktion zum Herunterladen einer Datei
const downloadFile = (filename) => {
  window.location.href = `/files/${filename}`;
};

// Dateien beim Laden der Komponente abrufen
onMounted(() => {
  fetchFiles();
});
</script>

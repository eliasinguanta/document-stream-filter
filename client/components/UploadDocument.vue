<template>
  <div class="container mt-5">

    <!-- Table displaying uploaded documents only if there are documents -->
    <div v-if="uploadedDocuments.length > 0">
      <table class="table">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">Name</th>
            <th scope="col">Size</th>
            <th scope="col">Actions</th>
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
      <input type="file" class="form-control" @change="handleFileUpload" ref="fileInput" />
    </div>

    <!-- Button to upload the document -->
    <button class="btn btn-primary" @click="uploadDocument">Upload Document</button>

  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      selectedFile: null,
      uploadedDocuments: [],
    };
  },
  created() {
    this.fetchFiles();
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadDocument() {
      if (!this.selectedFile) {
        alert("Please select a file to upload.");
        return;
      }
      if (this.selectedFile.type !== "text/plain") {
        alert("Please select a text file");
        this.selectedFile = null;
        this.$refs.fileInput.value = null;
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        const response = await fetch("/files", {
          method: "POST",
          body: formData,
        });

        if (response.ok) this.fetchFiles();
        else alert("Upload failed: " + response.status);

      } catch (error) {
        alert("An error occurred while uploading the file." + error);
      }

      this.selectedFile = null;
      this.$refs.fileInput.value = null;
    },
    async fetchFiles() {
      try {
        const response = await fetch("/files");
        const data = await response.json();
        this.uploadedDocuments = data.files.map((file) => ({ name: file.documentName, size: file.size, }));
      } catch (error) {
        alert("Error fetching files from:" + error.message);
      }
    },
    async deleteFile(filename) {
      try {
        const response = await fetch(`/files/${filename}`, {
          method: "DELETE",
        });

        if (response.ok) {
          console.log(`File ${filename} deleted successfully`);
          this.fetchFiles();
        } else {
          alert("Error deleting file.");
        }
      } catch (error) {
        console.error("Error deleting file:", error);
        alert("An error occurred while deleting the file.");
      }
    },
    async downloadFile(filename) {
      window.location.href = `/files/${filename}`;
    },
  },
};
</script>

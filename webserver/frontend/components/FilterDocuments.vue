<template>
    <div class="container mt-5">

        <!-- Button zum Anwenden der Filter -->
        <div class="mb-4">
            <button @click="applyFilters" class="btn btn-primary">Apply filter</button>
        </div>

        <!-- Tabelle der Queries und der Anzahl der Treffer -->
        <table class="table table-striped" v-if="queryResults.length > 0">
            <thead>
                <tr>
                    <th scope="col">Word</th>
                    <th scope="col">Metric</th>
                    <th scope="col">Distance</th>
                    <th scope="col">Documents</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(qr, index) in queryResults" :key="index">
                    <td>{{ qr.query.word }}</td>
                    <td>{{ qr.query.metric }}</td>
                    <td>{{ qr.query.distance }}</td>
                    <td>
                        <ul class="list-group">
                            <li v-for="(result) in qr.results" class="list-group-item d-flex justify-content-between align-items-center">
                                {{ result.documentName }}
                                <button @click="downloadDocument" class="btn btn-sm btn-success">Download</button>
                            </li>
                        </ul>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// result list
const queryResults = ref([]);

// request to the server to get the filtered documents
const applyFilters = async () => {
  try {
    const response = await fetch('/filter');
    if (!response.ok) throw new Error(`Serverfehler: ${response.status}`);
    
    const data = await response.json();
    queryResults.value = data;
  } catch (error) {
    console.error("Fehler beim Abrufen der gefilterten Dokumente:", error);
  }
};


// TODO: implement as http request to the server
const downloadDocument = async (documentName) => {
  alert("not implemented yet");
};
</script>
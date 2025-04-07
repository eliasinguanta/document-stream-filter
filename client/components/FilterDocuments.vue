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
                    <td>{{ qr.query.distanz }}</td>
                    <td>
                        <ul class="list-group">
                            <li v-for="(result, index) in qr.results" :key="index" class="list-group-item d-flex justify-content-between align-items-center">
                                {{ result.name }}
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

// example to see the frontend 
// TODO: delete
const queries = ref([
  { word: 'hallo', metric: 'edit', distanz: 2 },
  { word: 'meeting', metric: 'exact', distanz: 0 },
  { word: 'projekt', metric: 'hamming', distanz: 1 },
]);

// example to see the frontend
// TODO: delete
const documents = ref([
  { name: 'Dokument1.txt', size: '1.2 MB', content: 'Hallo Welt, dies ist ein Beispiel.' },
  { name: 'Dokument2.txt', size: '850 KB', content: 'Projektbesprechung am Freitag.' },
  { name: 'Dokument3.txt', size: '3.1 MB', content: 'Wir arbeiten am neuen Projekt.' },
  { name: 'Dokument4.txt', size: '450 KB', content: 'Hallo zusammen, willkommen im Meeting.' },
]);

// result list
const queryResults = ref([]);

// example filter to see the frontend
// TODO: change to http request to the server
const applyFilters = () => {
  const results = [];
  queries.value.forEach(query => {
    const filtered = documents.value.filter(doc => {
      return doc.content.toLowerCase().includes(query.word.toLowerCase());
    });

    results.push({ query, results: filtered });
  });

  queryResults.value = results;
};

// TODO: implement as http request to the server
const downloadDocument = async (documentName) => {
  alert("not implemented yet");
};
</script>
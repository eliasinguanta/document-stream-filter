<template>
    <div class="container mt-5">

        <!-- Button zum Anwenden der Filter -->
        <div class="mb-4">
            <button @click="applyFilters" class="btn btn-primary">Apply filter</button>
        </div>

        <!-- Tabelle mit paginierten Ergebnissen -->
        <table class="table table-striped" v-if="paginatedResults.length > 0">
            <thead>
                <tr>
                    <th scope="col">Word</th>
                    <th scope="col">Metric</th>
                    <th scope="col">Distance</th>
                    <th scope="col">Documents</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(qr, index) in paginatedResults.filter(q => q.results.length > 0)" :key="index">
                    <td>{{ qr.query.word }}</td>
                    <td>{{ qr.query.metric }}</td>
                    <td>{{ qr.query.distance }}</td>
                    <td>
                        <ul class="list-group">
                            <li v-for="(result) in qr.results.slice(0, 20)" :key="result.documentName"
                                class="list-group-item d-flex justify-content-between align-items-center">
                                {{ result.documentName }}
                                <button @click="downloadDocument(result.documentName)"
                                    class="btn btn-sm btn-success">Download</button>
                            </li>

                        </ul>
                    </td>
                </tr>
            </tbody>
        </table>

        <!-- Seiten-Navigation -->
        <div v-if="totalPages > 1">
            <nav aria-label="Page navigation">
                <ul class="pagination justify-content-center mt-4">
                    <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <button class="page-link" @click="goToPage(currentPage - 1)">Previous</button>
                    </li>
                    <li class="page-item" v-for="page in totalPages" :key="page"
                        :class="{ active: currentPage === page }">
                        <button class="page-link" @click="goToPage(page)">{{ page }}</button>
                    </li>
                    <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                        <button class="page-link" @click="goToPage(currentPage + 1)">Next</button>
                    </li>
                </ul>
            </nav>
        </div>

    </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// result list of the filter
const queryResults = ref([]);

// Pagination variables
const currentPage = ref(1);
const pageSize = 10;

// pagination function
const totalPages = computed(() => {
    return Math.ceil(queryResults.value.length / pageSize);
});

// pagination function
const paginatedResults = computed(() => {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return queryResults.value.slice(start, end);
});

// pagination function
const goToPage = (page) => {
    if (page < 1 || page > totalPages.value) return;
    currentPage.value = page;
};

// send a http request for filtered documents to the server
const applyFilters = async () => {
    try {
        const response = await fetch('/filter');
        if (!response.ok) throw new Error(`Serverfehler: ${response.status}`);
        queryResults.value = await response.json();

        //switch back to the first page (maybe we only have one)
        currentPage.value = 1;
    } catch (error) {
        console.error("Fehler beim Abrufen der gefilterten Dokumente:", error);
    }
};

const downloadDocument = (filename) => {
  window.location.href = `/files/${filename}`;
};
</script>
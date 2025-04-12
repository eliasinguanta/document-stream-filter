<template>
  <div class="container mt-5">

    <!-- Table of uploaded queries -->
    <div v-if="queries.length > 0">
      <table class="table mt-4">
        <thead>
          <tr>
            <th></th>
            <th>Word</th>
            <th>Metric</th>
            <th>Distance</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(query, index) in paginatedQueries" :key="query.id">
            <td>{{ (queryPage - 1) * queryPageSize + index + 1 }}</td>
            <td>{{ query.word }}</td>
            <td>{{ query.metric }}</td>
            <td>{{ query.distance }}</td>
            <td>
              <button type="button" class="btn btn-danger" @click="deleteQuery(query.queryId)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Controls -->
      <div class="d-flex justify-content-between align-items-center mt-3">
        <button class="btn btn-secondary" :disabled="queryPage === 1" @click="queryPage--">Zurück</button>
        <span>Seite {{ queryPage }} von {{ queryTotalPages }}</span>
        <button class="btn btn-secondary" :disabled="queryPage === queryTotalPages" @click="queryPage++">Weiter</button>
      </div>
    </div>

    <div class="mt-4">

      <!-- Form to upload a new query -->
      <form @submit.prevent="submitQuery" class="p-4 bg-light rounded shadow-sm w-100">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Word</label>
            <input v-model="word" type="text" class="form-control" placeholder="some word" required />
          </div>

          <div class="col-md-3">
            <label class="form-label" for="distance">Distance</label>
            <input id="distance" v-model.number="distance" type="number" class="form-control" min="0" step="1"
              required />
          </div>

          <div class="col-md-3">
            <label class="form-label" for="metric">Metric</label>
            <select v-model="metric" id="metric" class="form-control" required>
              <option value="edit">Edit</option>
              <option value="hamming">Hamming</option>
              <option value="exact">Exact</option>
            </select>
          </div>
        </div>

        <div class="mt-4">
          <button type="submit" class="btn btn-primary">Upload Query</button>
        </div>
      </form>
    </div>

  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'

const word = ref('')
const distance = ref(1.0)
const metric = ref('edit')
const queries = ref([])
const queryPage = ref(1)
const queryPageSize = ref(5)

// Total number of pages for the queries
const queryTotalPages = computed(() => {
  return Math.ceil(queries.value.length / queryPageSize.value)
})

// queries to be displayed on the paginated page
const paginatedQueries = computed(() => {
  const start = (queryPage.value - 1) * queryPageSize.value
  const end = start + queryPageSize.value
  return queries.value.slice(start, end)
})

// Load queries from the server
// This function is called when the component is mounted
const loadQueries = async () => {
  try {
    const res = await fetch('/queries')
    if (!res.ok) throw new Error("http response is not okay");
    const data = await res.json()
    queries.value = data
  } catch (err) {
    console.error('Error fetching loading the queries:', err);
  }
}

// Submit a new query to the server
// This function is called when the form is submitted
// A new query contains a word, a metric, and a distance
const submitQuery = async () => {

  // Validate the input
  if (word.value.trim() === '') return

  const newQuery = {
    word: word.value.trim(),
    metric: metric.value,
    distance: distance.value
  }

  // Send the new query to the server
  const res = await fetch('/queries', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(newQuery)
  })

  // Check if the response is okay
  if (!res.ok) console.error('error for creating query')

  // Parse the response and add the new query to the list
  const createdQuery = await res.json()
  queries.value.push(createdQuery)

  // Reset the form fields
  word.value = ''
  distance.value = 1.0
  metric.value = 'edit'

}

// Delete a query from the server
// This function is called when the delete button is clicked
// The query is identified by its ID
const deleteQuery = async (queryId) => {

  // http DELETE request to the server
  const res = await fetch(`/queries/${queryId}`, { method: 'DELETE' });
  if (!res.ok) console.error('error for deleting query')

  // Parse the response and remove the query from the list
  else queries.value = queries.value.filter(query => query.queryId !== queryId)

}

onMounted(() => {
  loadQueries()
})
</script>

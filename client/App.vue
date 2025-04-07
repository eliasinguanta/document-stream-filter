<template>
  <div id="app">
    <h1 class="text-center mb-4">Document Stream Filter</h1>
    <div class="row justify-content-center">
      <div class="col-md-5">
        <UploadDocument />
      </div>
      <div class="col-md-5">
        <UploadQuery />
      </div>
    </div>
  </div>
</template>

<script>
import UploadDocument from './components/UploadDocument.vue';
import UploadQuery from './components/UploadQuery.vue';
export default {
  name: 'App',
  components: {
    UploadDocument,
    UploadQuery,
  },
};
</script>

<style>
#app {
  text-align: center;
  padding: 20px;
}

h1 {
  color: #42b983;
}
</style>

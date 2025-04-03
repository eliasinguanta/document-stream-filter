<template>
  <div id="app">
    <h1>Document Stream Filter</h1>
    <UploadDocument />
  </div>
</template>

<script>
import UploadDocument from './components/UploadDocument.vue';

export default {
  name: 'App',
  components: {
    UploadDocument,
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

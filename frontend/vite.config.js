import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  root: './', 
  build: {
    outDir: './dist',  
    emptyOutDir: true,  
  },
  base: "/website/", // base path for the website
});

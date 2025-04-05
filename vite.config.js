import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import fs from 'fs';

export default defineConfig({
  plugins: [vue()],
  root: 'client', 
  build: {
    outDir: '../dist',  
    emptyOutDir: true,  
  },
  base: "./", 

});

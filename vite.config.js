import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import fs from 'fs';

export default defineConfig({
  plugins: [vue()],
  root: 'client',  // Setzt den Root-Ordner auf 'client'
  build: {
    outDir: '../dist',  // Output-Verzeichnis für gebaute Dateien
    emptyOutDir: true,  // Löscht vorherige Builds, um alte Dateien zu entfernen
  },
  base: "./", // Verhindert absolute Pfade in der index.html
  server: {
    https: {
      key: fs.readFileSync('ssl/server.key'),
      cert: fs.readFileSync('ssl/server.crt'),
    },
  }
});

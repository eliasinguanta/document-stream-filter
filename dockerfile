# 1. Offizielles Node.js-Image als Basis
FROM node:18-alpine

# 2. Setze das Arbeitsverzeichnis
WORKDIR /app

# 3. Kopiere die Package-Dateien und installiere nur Produktionsabhängigkeiten
COPY package.json package-lock.json ./
RUN npm install --omit=dev

# 4. Kopiere den Rest des Codes
COPY . .

# 5. Baue die Vite-App
RUN npm run build

# 6. Exponiere den Port für den Express-Server
EXPOSE 3000

# 7. Startbefehl für den Container
CMD ["npm", "start"]

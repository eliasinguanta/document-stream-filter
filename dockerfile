# Offizielles Node.js-Image als Basis
FROM node:18-alpine


# Installiere AWS CLI direkt über Alpine-Paketmanager
RUN apk update && apk add --no-cache \
    aws-cli \
    curl \
    unzip \
    && rm -rf /var/cache/apk/*

# Lade AWS CLI v2 herunter und installiere es
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/

# set aws config
ENV AWS_ACCESS_KEY_ID=AKIAVUDEFQ2QWMOBCWXR
ENV AWS_SECRET_ACCESS_KEY=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
ENV AWS_REGION=eu-north-1

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die Package-Dateien und installiere nur Produktionsabhängigkeiten
COPY package.json package-lock.json ./
RUN npm install --omit=dev
RUN npm install vite
RUN npm install @aws-sdk/client-s3
RUN npm install multer
RUN npm install @aws-sdk/client-dynamodb
RUN npm install @aws-sdk/util-dynamodb
RUN npm install formidable





# Kopiere den Rest des Codes
COPY . .

# Baue die Vite-App
RUN npm run build

# Exponiere den Port für den Express-Server
EXPOSE 3000

# Startbefehl für den Container
CMD ["npm", "start"]

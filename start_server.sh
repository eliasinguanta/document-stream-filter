#!/bin/bash

# get ip
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "localhost")

# make ip available for vite
echo "VITE_API_URL=https://$PUBLIC_IP:3000" > ./client/.env

# start the server
npm run start

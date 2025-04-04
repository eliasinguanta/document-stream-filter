#!/bin/bash

# get ip
#PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "localhost")
PUBLIC_IP=127.0.0.1 #for testing

# make ip available for vite
touch ./client/.env
echo "VITE_API_URL=https://$PUBLIC_IP:3000" > ./client/.env

# start the server
npm run start

#!/bin/bash

sudo apt-get update
sudo apt-get install -y docker.io

sudo usermod -aG docker ubuntu
newgrp docker


sudo apt install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf awscliv2.zip aws/
aws configure
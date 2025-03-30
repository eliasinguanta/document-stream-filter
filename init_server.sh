#!/bin/bash

sudo apt-get update
sudo apt-get install -y docker.io

sudo usermod -aG docker ubuntu
newgrp docker
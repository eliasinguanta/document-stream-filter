#!/bin/bash

export AWS_ACCESS_KEY_ID="" #TODO: Add AWS access key
export AWS_SECRET_ACCESS_KEY="" #TODO: Add AWS secret key
export AWS_REGION="eu-north-1"

sudo apt-get update
sudo apt-get install -y docker.io

sudo usermod -aG docker ubuntu
sudo systemctl restart docker

sudo apt install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2.zip aws/

export REPO_OWNER="eliasinguanta"
export REPO_NAME="document-stream-filter"

export CI_CD_ACCESS_TOKEN=$(aws ssm get-parameter --name "/github/dsf/ci_cd_access_token" --query "Parameter.Value" --output text)


cat <<EOF > /home/ubuntu/update_container.sh
#!/bin/bash

export REPO_OWNER="eliasinguanta"
export REPO_NAME="document-stream-filter"
echo "$CI_CD_ACCESS_TOKEN" | docker login ghcr.io -u $REPO_OWNER --password-stdin

docker pull ghcr.io/\$REPO_OWNER/\$REPO_NAME:latest

docker stop \$REPO_NAME || true
docker rm \$REPO_NAME || true

docker run -d --name \$REPO_NAME -p 80:3000 ghcr.io/\$REPO_OWNER/\$REPO_NAME:latest
echo "[\$(date)] Update abgeschlossen!" >> /home/ubuntu/update_container.log
EOF

chmod +x /home/ubuntu/update_container.sh

(crontab -l 2>/dev/null; echo "*/1 * * * * /home/ubuntu/update_container.sh >> /home/ubuntu/update_container.log 2>&1") | crontab -



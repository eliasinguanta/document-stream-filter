aws ecr create-repository --repository-name dsf-filter
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 386757133985.dkr.ecr.eu-north-1.amazonaws.com
docker build -t dsf-filter .
docker tag dsf-filter 386757133985.dkr.ecr.eu-north-1.amazonaws.com/dsf-filter:latest
docker push 386757133985.dkr.ecr.eu-north-1.amazonaws.com/dsf-filter:latest



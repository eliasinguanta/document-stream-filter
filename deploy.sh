#!/bin/bash
# This script builds the infrastructure and deploys the application to an EKS cluster.
# The Container are loaded from ecr they are not build in this script.
terraform -chdir=terraform init
terraform -chdir=terraform apply -auto-approve
aws eks update-kubeconfig --region eu-north-1 --name document-filter-cluster

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx


for i in {1..30}; do
  export HOST=$(kubectl get svc ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  
  if [[ -n "$HOST" ]]; then
    echo "Gefundener LoadBalancer Host: $HOST"
    break
  fi

  echo "Noch kein Hostname verfügbar, versuche erneut..."
  sleep 5
done

if [[ -z "$HOST" ]]; then
  echo "Fehler: Kein LoadBalancer-Hostname gefunden."
  exit 1
fi

until kubectl get endpoints ingress-nginx-controller-admission -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q '[0-9]'; do
  sleep 2
  echo -n "."
done

for chart in documents queries filter website; do
  cp ./k8s/charts/$chart/values.yaml ./k8s/charts/$chart/tmp-values.yaml
  sed -i "s/REPLACE_HOST/$HOST/g" ./k8s/charts/$chart/tmp-values.yaml
  helm upgrade --install dsf-$chart ./k8s/charts/$chart -f ./k8s/charts/$chart/tmp-values.yaml
  rm ./k8s/charts/$chart/tmp-values.yaml
done
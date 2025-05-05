#!/bin/bash
# This script deletes the infrastructure and removes the application from the EKS cluster.

# delete the application from the EKS cluster
helm list -q | xargs -r helm uninstall

# delete the infrastructure
terraform -chdir=terraform destroy -auto-approve

# clean up the local environment
find . -type d -name ".terraform" -exec rm -rf {} +
find . -type f -name "*.tfstate" -delete
find . -type f -name "*.tfstate.backup" -delete
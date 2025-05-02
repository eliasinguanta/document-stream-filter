helm list -q | xargs -r helm uninstall
terraform -chdir=terraform destroy -auto-approve
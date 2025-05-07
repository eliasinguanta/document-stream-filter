terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = "eu-north-1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "document-filter-vpc"
  cidr = "10.10.0.0/16"

  azs            = ["eu-north-1a", "eu-north-1b"]
  public_subnets = ["10.10.101.0/24", "10.10.102.0/24"]

  enable_nat_gateway        = false
  enable_vpn_gateway        = false
  map_public_ip_on_launch   = true
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.0.0"

  cluster_name                   = "document-filter-cluster"
  cluster_version                = "1.32"
  subnet_ids                     = module.vpc.public_subnets
  vpc_id                         = module.vpc.vpc_id
  cluster_endpoint_public_access = true
  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    default = {
      name           = "document-filter-nodes"
      desired_size   = 1
      max_size       = 2
      min_size       = 1
      instance_types = ["t3.small"]
      subnet_ids     = module.vpc.public_subnets
    }
  }
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_name" {
  value = module.eks.cluster_name
}

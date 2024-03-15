terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.41.1"
    }
  }

  required_version = "~>1.7.5"
}

terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "= 4.6.0"
    }
    external = {
      source  = "hashicorp/external"
      version = "= 2.3.5"
    }
  }
}

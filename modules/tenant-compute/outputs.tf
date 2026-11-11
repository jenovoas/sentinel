output "tenant_id" {
  value = var.tenant_id
}

output "request_id" {
  value = var.request_id
}

output "container_id" {
  value = docker_container.tenant.id
}

output "network_id" {
  value = docker_network.tenant.id
}

output "storage_preflight" {
  value = {
    verified         = var.storage_preflight_verified
    filesystem_bytes = var.storage_filesystem_bytes
    host_free_bytes  = var.storage_host_free_bytes
  }
}

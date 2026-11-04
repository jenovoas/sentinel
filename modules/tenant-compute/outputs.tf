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
    verified           = data.external.storage_preflight.result.verified
    filesystem_bytes   = tonumber(data.external.storage_preflight.result.filesystem_bytes)
    host_free_bytes    = tonumber(data.external.storage_preflight.result.host_free_bytes)
  }
}

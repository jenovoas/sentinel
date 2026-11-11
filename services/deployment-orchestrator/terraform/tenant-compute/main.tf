terraform {
  backend "http" {}
}

module "tenant_compute" {
  source = "../../../../modules/tenant-compute"

  tenant_id                    = var.tenant_id
  request_id                   = var.request_id
  operation_id                 = var.operation_id
  image_digest                 = var.image_digest
  storage_path                 = var.storage_path
  disk_limit_bytes             = var.disk_limit_bytes
  min_host_free_bytes          = var.min_host_free_bytes
  cpu_limit                    = var.cpu_limit
  memory_limit_mb              = var.memory_limit_mb
  tmpfs_limit_mb               = var.tmpfs_limit_mb
  pilot_identity_authorized    = var.pilot_identity_authorized
  guacamole_acl_verified       = var.guacamole_acl_verified
  remote_backend_lock_verified = var.remote_backend_lock_verified
  capacity_approved            = var.capacity_approved
  docker_socket_path           = var.docker_socket_path
  storage_preflight_verified   = var.storage_preflight_verified
  storage_filesystem_bytes     = var.storage_filesystem_bytes
  storage_host_free_bytes      = var.storage_host_free_bytes
  edge_network_name            = var.edge_network_name
}

output "container_id" {
  value = module.tenant_compute.container_id
}
output "network_id" {
  value = module.tenant_compute.network_id
}
output "storage_preflight" {
  value = module.tenant_compute.storage_preflight
}

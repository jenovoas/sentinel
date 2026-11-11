provider "docker" {
  host = "unix://${var.docker_socket_path}"
}

resource "terraform_data" "deployment_gates" {
  input = {
    tenant_id    = var.tenant_id
    request_id   = var.request_id
    operation_id = var.operation_id
  }

  lifecycle {
    precondition {
      condition     = var.pilot_identity_authorized
      error_message = "Aprovisionamiento bloqueado: falta autorización de identidad piloto."
    }

    precondition {
      condition     = var.guacamole_acl_verified
      error_message = "Aprovisionamiento bloqueado: falta verificar la ACL de Guacamole."
    }

    precondition {
      condition     = var.remote_backend_lock_verified
      error_message = "Aprovisionamiento bloqueado: falta verificar el backend remoto con lock."
    }

    precondition {
      condition     = var.capacity_approved
      error_message = "Aprovisionamiento bloqueado: falta aprobar la capacidad del host."
    }

    precondition {
      condition     = var.storage_preflight_verified && var.storage_filesystem_bytes > 0 && var.storage_filesystem_bytes <= var.disk_limit_bytes && var.storage_host_free_bytes >= var.min_host_free_bytes
      error_message = "Aprovisionamiento bloqueado: la cuota dura no fue verificada."
    }
  }
}

resource "docker_image" "tenant" {
  name         = var.image_digest
  keep_locally = true

  depends_on = [terraform_data.deployment_gates]
}

resource "docker_network" "tenant" {
  name     = "${var.tenant_id}-${var.operation_id}"
  driver   = "bridge"
  internal = true
  ipv6     = false


  labels {
    label = "sentinel.tenant_id"
    value = var.tenant_id
  }

  labels {
    label = "sentinel.request_id"
    value = var.request_id
  }

  depends_on = [terraform_data.deployment_gates]
}

resource "docker_container" "tenant" {
  name  = "${var.tenant_id}-${var.operation_id}"
  image = docker_image.tenant.image_id

  cpus              = tostring(var.cpu_limit)
  memory            = var.memory_limit_mb
  memory_swap       = var.memory_limit_mb
  read_only         = true
  privileged        = false
  publish_all_ports = false
  restart           = "unless-stopped"
  must_run          = true
  log_driver        = "json-file"
  log_opts = {
    "max-size" = "10m"
    "max-file" = "3"
  }
  tmpfs = {
    "/tmp" = "rw,noexec,nosuid,size=${var.tmpfs_limit_mb}m"
  }
  security_opts = ["no-new-privileges:true"]

  capabilities {
    drop = ["ALL"]
  }

  volumes {
    host_path      = var.storage_path
    container_path = "/workspace"
    read_only      = false
  }

  networks_advanced {
    name = docker_network.tenant.name
  }
  dynamic "networks_advanced" {
    for_each = var.edge_network_name == "" ? [] : [var.edge_network_name]
    content {
      name = networks_advanced.value
    }
  }

  labels {
    label = "sentinel.tenant_id"
    value = var.tenant_id
  }

  labels {
    label = "sentinel.request_id"
    value = var.request_id
  }

  depends_on = [terraform_data.deployment_gates]
}

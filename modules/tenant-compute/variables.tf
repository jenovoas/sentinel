variable "tenant_id" {
  type = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{0,29}$", var.tenant_id))
    error_message = "tenant_id debe ser un identificador en minúsculas de hasta 30 caracteres."
  }
}

variable "request_id" {
  type = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$", var.request_id))
    error_message = "request_id debe ser un identificador válido de hasta 128 caracteres."
  }
}
variable "operation_id" {
  type = string

  validation {
    condition     = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", var.operation_id))
    error_message = "operation_id debe ser un UUID v4 generado por el runner."
  }
}


variable "image_digest" {
  type = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9._:/-]*@sha256:[0-9a-f]{64}$", var.image_digest))
    error_message = "image_digest debe identificar una imagen Docker mediante digest sha256 inmutable."
  }
}


variable "storage_path" {
  type = string

  validation {
    condition     = startswith(var.storage_path, "/") && var.storage_path != "/"
    error_message = "storage_path debe ser una ruta absoluta distinta de la raíz."
  }
}

variable "disk_limit_bytes" {
  type = number

  validation {
    condition     = var.disk_limit_bytes >= 1 && floor(var.disk_limit_bytes) == var.disk_limit_bytes
    error_message = "disk_limit_bytes debe ser un entero positivo."
  }
}

variable "min_host_free_bytes" {
  type    = number
  default = 1073741824

  validation {
    condition     = var.min_host_free_bytes >= 0 && floor(var.min_host_free_bytes) == var.min_host_free_bytes
    error_message = "min_host_free_bytes debe ser un entero no negativo."
  }
}

variable "cpu_limit" {
  type = number

  validation {
    condition     = var.cpu_limit > 0 && var.cpu_limit <= 64
    error_message = "cpu_limit debe estar entre 0 y 64 CPU."
  }
}

variable "memory_limit_mb" {
  type = number

  validation {
    condition     = var.memory_limit_mb >= 64 && floor(var.memory_limit_mb) == var.memory_limit_mb
    error_message = "memory_limit_mb debe ser un entero de al menos 64 MB."
  }
}

variable "tmpfs_limit_mb" {
  type    = number
  default = 64

  validation {
    condition     = var.tmpfs_limit_mb >= 1 && var.tmpfs_limit_mb <= 512 && floor(var.tmpfs_limit_mb) == var.tmpfs_limit_mb
    error_message = "tmpfs_limit_mb debe ser un entero entre 1 y 512 MB."
  }
}

variable "pilot_identity_authorized" {
  type    = bool
  default = false
}

variable "guacamole_acl_verified" {
  type    = bool
  default = false
}

variable "remote_backend_lock_verified" {
  type    = bool
  default = false
}

variable "capacity_approved" {
  type    = bool
  default = false
}

variable "docker_socket_path" {
  type    = string
  default = "/var/run/docker.sock"

  validation {
    condition     = startswith(var.docker_socket_path, "/") && var.docker_socket_path != "/" && !endswith(var.docker_socket_path, "/") && !strcontains(var.docker_socket_path, "//") && !contains(split("/", var.docker_socket_path), ".") && !contains(split("/", var.docker_socket_path), "..")
    error_message = "docker_socket_path debe ser una ruta Unix local absoluta, canónica y distinta de la raíz."
  }
}

variable "storage_preflight_verified" {
  type    = bool
  default = false
}

variable "storage_filesystem_bytes" {
  type    = number
  default = 0

  validation {
    condition     = var.storage_filesystem_bytes >= 0 && floor(var.storage_filesystem_bytes) == var.storage_filesystem_bytes
    error_message = "storage_filesystem_bytes debe ser un entero no negativo."
  }
}

variable "storage_host_free_bytes" {
  type    = number
  default = 0

  validation {
    condition     = var.storage_host_free_bytes >= 0 && floor(var.storage_host_free_bytes) == var.storage_host_free_bytes
    error_message = "storage_host_free_bytes debe ser un entero no negativo."
  }
}

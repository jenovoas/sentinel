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
    condition     = can(regex("^[a-z0-9][a-z0-9-]{0,31}$", var.request_id))
    error_message = "request_id debe ser un identificador en minúsculas de hasta 32 caracteres."
  }
}

variable "image_digest" {
  type = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9._:/-]*@sha256:[0-9a-f]{64}$", var.image_digest))
    error_message = "image_digest debe identificar una imagen Docker mediante digest sha256 inmutable."
  }
}

variable "tenant_cidr" {
  type = string

  validation {
    condition     = can(cidrnetmask(var.tenant_cidr)) && try(cidrhost(var.tenant_cidr, 0) == split("/", var.tenant_cidr)[0], false)
    error_message = "tenant_cidr debe ser una red IPv4 CIDR válida y canónica."
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

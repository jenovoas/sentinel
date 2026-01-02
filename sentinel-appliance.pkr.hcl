packer {
  required_plugins {
    qemu = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/qemu"
    }
  }
}

source "qemu" "sentinel-appliance" {
  # Usamos la imagen Cloud oficial (ya instalada)
  iso_url          = "https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2"
  iso_checksum     = "none" # Packer verificará la descarga, pero la imagen cloud cambia frecuentemente
  disk_image       = true
  
  ssh_username     = "debian"
  ssh_password     = "sentinel" # Se configurará via cloud-init
  ssh_timeout      = "10m"
  shutdown_command = "sudo shutdown -P now"
  
  vm_name          = "Sentinel-Cortex-v2.0"
  memory           = 2048
  cpus             = 2 # Un poco más de potencia para el Cortex
  disk_size        = "40G"
  format           = "qcow2"
  headless         = true
  accelerator      = "kvm"

  # Configuración desatendida via Cloud-Init (Seed ISO virtual)
  qemuargs = [
    ["-smbios", "type=1,serial=ds=nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/"]
  ]
  
  http_directory   = "http/cloud-init"
}

build {
  sources = ["source.qemu.sentinel-appliance"]

  provisioner "shell" {
    inline = [
      "echo '🚀 Preparando el sistema soberano...'",
      "sudo apt-get update",
      "sudo apt-get install -y git curl docker.io",
      "sudo mkdir -p /opt/sentinel",
      "sudo chown debian:debian /opt/sentinel"
    ]
  }

  provisioner "shell-local" {
    inline = [
      "echo '📦 Empaquetando código fuente (excluyendo .venv y logs)...'",
      "tar --exclude='./.venv' --exclude='./logs' --exclude='./output-sentinel-appliance' -czf sentinel-dist.tar.gz ./"
    ]
  }

  provisioner "file" {
    source      = "sentinel-dist.tar.gz"
    destination = "/tmp/sentinel-dist.tar.gz"
  }

  provisioner "shell" {
    inline = [
      "echo '🔓 Desempaquetando en el appliance...'",
      "sudo tar -xzf /tmp/sentinel-dist.tar.gz -C /opt/sentinel",
      "sudo rm /tmp/sentinel-dist.tar.gz",
      "echo '🚀 Ejecutando Master Gold Installer...'",
      "cd /opt/sentinel && sudo bash tools/sentinel-gold-install.sh"
    ]
  }

  post-processor "shell-local" {
    inline = [
      "echo '💿 Finalizando Appliance: Generando imagen final...'",
      "qemu-img convert -f qcow2 -O vmdk output-sentinel-appliance/Sentinel-Cortex-v2.0 Sentinel-Cortex-v2.0.vmdk",
      "echo '✨ Appliance generado exitosamente: Sentinel-Cortex-v2.0.vmdk'"
    ]
  }
}

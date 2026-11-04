import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

from tenant_compute_storage_preflight import LOOP_DEVICE, decode_mount_field, find_mount, inspect_storage


TENANT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,29}$")
BLOCK_SIZE = 4096
DEFAULT_MIN_HOST_FREE_BYTES = 1073741824


@dataclass(frozen=True)
class StoragePaths:
    image_root: Path = Path("/var/lib/sentinel/tenant-storage")
    mount_root: Path = Path("/srv/sentinel/tenants")
    unit_root: Path = Path("/etc/systemd/system")


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def target_paths(tenant_id, paths):
    if not TENANT_RE.fullmatch(tenant_id):
        raise ValueError("tenant_id inválido")
    return paths.image_root / f"{tenant_id}.ext4", paths.mount_root / tenant_id


def validate_size(size_bytes, min_host_free_bytes):
    if size_bytes <= 0 or size_bytes % BLOCK_SIZE:
        raise ValueError("size_bytes debe ser positivo y múltiplo de 4096")
    if min_host_free_bytes < 0:
        raise ValueError("min_host_free_bytes debe ser no negativo")


def path_is_canonical(path):
    return path.is_absolute() and path.resolve(strict=False) == path


def ensure_secure_directory(path, mode):
    if not path_is_canonical(path):
        raise ValueError(f"la ruta de directorio no es canónica: {path}")
    path.mkdir(mode=mode, parents=True, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise ValueError(f"el directorio debe pertenecer al usuario efectivo y no ser escribible por grupo/otros: {path}")


def mount_count(mountinfo, mount_path):
    count = 0
    for line in mountinfo.splitlines():
        before, separator, _ = line.partition(" - ")
        fields = before.split()
        if separator and len(fields) >= 6 and decode_mount_field(fields[4]) == str(mount_path):
            count += 1
    return count


def image_type(image_path, run_command):
    result = run_command(["blkid", "-p", "-s", "TYPE", "-o", "value", str(image_path)])
    return result.stdout.strip()


def verify_image(image_path, size_bytes, run_command):
    if image_path.is_symlink() or not image_path.is_file():
        raise ValueError("la imagen debe ser un archivo regular sin enlaces simbólicos")
    image_stat = image_path.stat()
    if image_stat.st_uid != os.geteuid() or image_stat.st_mode & 0o077:
        raise ValueError("la imagen debe pertenecer al usuario efectivo y no ser accesible por grupo/otros")
    if image_stat.st_size != size_bytes:
        raise ValueError("la imagen existente tiene un tamaño distinto al solicitado")
    if image_stat.st_blocks * 512 < image_stat.st_size:
        raise ValueError("la imagen existente no está completamente preasignada")
    if image_type(image_path, run_command) != "ext4":
        raise ValueError("la imagen existente no contiene un sistema de archivos ext4")


def create_image(image_path, size_bytes, min_host_free_bytes, run_command, statvfs):
    image_path.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    if image_path.is_symlink() or image_path.exists():
        verify_image(image_path, size_bytes, run_command)
        return False

    host = statvfs(str(image_path.parent))
    free_bytes = host.f_bavail * host.f_frsize
    if free_bytes < size_bytes + min_host_free_bytes:
        raise ValueError("el espacio libre del host no cubre imagen y margen operativo")

    descriptor, temporary_name = tempfile.mkstemp(prefix=".tenant-storage-", dir=image_path.parent)
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        os.chmod(temporary_path, 0o600)
        run_command(["fallocate", "--length", str(size_bytes), str(temporary_path)])
        allocated = temporary_path.stat()
        if allocated.st_size != size_bytes or allocated.st_blocks * 512 < size_bytes:
            raise ValueError("fallocate no reservó físicamente toda la imagen")
        run_command(["mkfs.ext4", "-F", "-m", "0", "-E", "nodiscard", str(temporary_path)])
        run_command(["fallocate", "--length", str(size_bytes), str(temporary_path)])
        formatted = temporary_path.stat()
        if formatted.st_size != size_bytes or formatted.st_blocks * 512 < size_bytes:
            raise ValueError("la imagen ext4 no conserva la preasignación física completa")
        if image_type(temporary_path, run_command) != "ext4":
            raise ValueError("mkfs.ext4 no produjo una imagen ext4 verificable")
        with temporary_path.open("rb") as handle:
            os.fsync(handle.fileno())
        os.link(temporary_path, image_path, follow_symlinks=False)
    finally:
        temporary_path.unlink(missing_ok=True)
    verify_image(image_path, size_bytes, run_command)
    directory_fd = os.open(image_path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return True


def render_mount_unit(image_path, mount_path, tenant_id, run_command):
    unit_name = run_command([
        "systemd-escape", "--path", "--suffix=mount", str(mount_path),
    ]).stdout.strip()
    if not unit_name or "/" in unit_name or not unit_name.endswith(".mount"):
        raise ValueError("systemd-escape devolvió un nombre de unidad inválido")
    content = (
        "[Unit]\n"
        f"Description=Almacenamiento tenant {tenant_id}\n\n"
        "[Mount]\n"
        f"What={image_path}\n"
        f"Where={mount_path}\n"
        "Type=ext4\n"
        "Options=loop,nodev,nosuid\n\n"
        "[Install]\n"
        "WantedBy=local-fs.target\n"
    )
    return unit_name, content


def validate_unit_file(unit_path, content):
    if unit_path.is_symlink():
        raise ValueError("la unidad systemd existente no puede ser un enlace simbólico")
    if not unit_path.exists():
        return False
    info = unit_path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise ValueError("la unidad systemd debe pertenecer al usuario efectivo y no ser escribible por grupo/otros")
    if unit_path.read_text() != content:
        raise ValueError("ya existe una unidad systemd distinta para este punto de montaje")
    return True


def write_unit(unit_path, content):
    unit_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    if validate_unit_file(unit_path, content):
        return False

    descriptor, temporary_name = tempfile.mkstemp(prefix=".tenant-mount-", dir=unit_path.parent)
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_path, unit_path, follow_symlinks=False)
        directory_fd = os.open(unit_path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary_path.unlink(missing_ok=True)
    return True


def verify_mounted_storage(tenant_id, image_path, mount_path, size_bytes, min_host_free_bytes, mountinfo, run_command, statvfs):
    if mount_count(mountinfo, mount_path) != 1:
        raise ValueError("el punto de montaje debe aparecer exactamente una vez")
    mount = find_mount(mountinfo, str(mount_path))
    if mount["filesystem"] != "ext4" or not LOOP_DEVICE.fullmatch(mount["source"]):
        raise ValueError("se requiere un montaje ext4 respaldado por loop")
    backing = run_command([
        "losetup", "--noheadings", "--output", "BACK-FILE", "--raw", mount["source"],
    ]).stdout.strip()
    if not backing or Path(backing).resolve(strict=True) != image_path.resolve(strict=True):
        raise ValueError("el montaje activo no corresponde a la imagen del tenant")
    result = inspect_storage(
        {
            "mount_path": str(mount_path),
            "max_bytes": str(size_bytes),
            "min_host_free_bytes": str(min_host_free_bytes),
        },
        mountinfo,
        backing,
        statvfs=statvfs,
    )
    return result


def provision_storage(tenant_id, size_bytes, min_host_free_bytes, paths, run_command=command, statvfs=os.statvfs, mountinfo=None):
    validate_size(size_bytes, min_host_free_bytes)
    image_path, mount_path = target_paths(tenant_id, paths)
    if not path_is_canonical(image_path) or not path_is_canonical(mount_path):
        raise ValueError("las rutas de almacenamiento no son canónicas")
    ensure_secure_directory(paths.image_root, 0o750)
    ensure_secure_directory(paths.mount_root, 0o750)
    ensure_secure_directory(paths.unit_root, 0o755)

    unit_name, unit_content = render_mount_unit(image_path, mount_path, tenant_id, run_command)
    unit_path = paths.unit_root / unit_name
    if not path_is_canonical(unit_path):
        raise ValueError("la ruta de la unidad systemd no es canónica")
    validate_unit_file(unit_path, unit_content)

    if mountinfo is None:
        mountinfo = Path("/proc/self/mountinfo").read_text()
    active_mounts = mount_count(mountinfo, mount_path)
    if active_mounts > 1:
        raise ValueError("el punto de montaje tiene montajes ambiguos")
    if active_mounts == 1:
        verify_image(image_path, size_bytes, run_command)
        result = verify_mounted_storage(
            tenant_id, image_path, mount_path, size_bytes, min_host_free_bytes,
            mountinfo, run_command, statvfs,
        )
        created_unit = write_unit(unit_path, unit_content)
        run_command(["systemctl", "daemon-reload"])
        run_command(["systemctl", "enable", "--now", unit_name])
        return {
            **result,
            "unit_name": unit_name,
            "unit_created": str(created_unit).lower(),
            "status": "verified_and_persistent",
        }

    if mount_path.is_symlink() or (mount_path.exists() and not mount_path.is_dir()):
        raise ValueError("el punto de montaje debe ser un directorio real y canónico")
    if mount_path.exists() and any(mount_path.iterdir()):
        raise ValueError("el punto de montaje sin montar debe estar vacío")

    created_image = create_image(image_path, size_bytes, min_host_free_bytes, run_command, statvfs)
    mount_path.mkdir(mode=0o750, parents=True, exist_ok=True)
    if not path_is_canonical(mount_path):
        raise ValueError("el punto de montaje debe ser un directorio real y canónico")
    created_unit = write_unit(unit_path, unit_content)
    run_command(["systemctl", "daemon-reload"])
    run_command(["systemctl", "enable", "--now", unit_name])
    return {
        "verified": "false",
        "tenant_id": tenant_id,
        "image_path": str(image_path),
        "mount_path": str(mount_path),
        "unit_name": unit_name,
        "image_created": str(created_image).lower(),
        "unit_created": str(created_unit).lower(),
        "status": "mount_requested",
    }


def main():
    parser = argparse.ArgumentParser(description="Aprovisiona almacenamiento ext4 tenant de forma conservadora")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--size-bytes", required=True, type=int)
    parser.add_argument("--min-host-free-bytes", type=int, default=DEFAULT_MIN_HOST_FREE_BYTES)
    parser.add_argument("--apply", action="store_true", help="crear la imagen e instalar/iniciar la unidad systemd")
    args = parser.parse_args()
    try:
        validate_size(args.size_bytes, args.min_host_free_bytes)
        image_path, mount_path = target_paths(args.tenant_id, StoragePaths())
        if not args.apply:
            print(json.dumps({
                "status": "planned",
                "tenant_id": args.tenant_id,
                "image_path": str(image_path),
                "mount_path": str(mount_path),
                "size_bytes": args.size_bytes,
                "min_host_free_bytes": args.min_host_free_bytes,
                "apply_required": True,
            }))
            return 0
        if os.geteuid() != 0:
            raise PermissionError("--apply requiere privilegios de root")
        result = provision_storage(
            args.tenant_id,
            args.size_bytes,
            args.min_host_free_bytes,
            StoragePaths(),
        )
        print(json.dumps(result))
    except (OSError, PermissionError, subprocess.SubprocessError, ValueError) as error:
        print(f"Aprovisionamiento de almacenamiento bloqueado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

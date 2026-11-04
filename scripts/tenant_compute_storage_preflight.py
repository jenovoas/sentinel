import json
import os
from pathlib import Path
import re
import subprocess
import sys


LOOP_DEVICE = re.compile(r"^/dev/loop[0-9]+$")


def decode_mount_field(value):
    return re.sub(
        r"\\([0-7]{3})",
        lambda match: chr(int(match.group(1), 8)),
        value,
    )


def find_mount(mountinfo, target):
    matches = []
    for line in mountinfo.splitlines():
        before, separator, after = line.partition(" - ")
        if not separator:
            continue
        fields = before.split()
        filesystem = after.split()
        if len(fields) < 6 or len(filesystem) < 3:
            continue
        if decode_mount_field(fields[4]) == target:
            matches.append({
                "filesystem": filesystem[0],
                "source": decode_mount_field(filesystem[1]),
                "mount_options": fields[5].split(","),
                "super_options": filesystem[2].split(","),
            })
    if len(matches) != 1:
        raise ValueError("la ruta debe tener exactamente un punto de montaje activo")
    return matches[0]


def inspect_storage(query, mountinfo, backing_file, statvfs=os.statvfs):
    raw_path = query.get("mount_path", "")
    if not raw_path or not os.path.isabs(raw_path):
        raise ValueError("mount_path debe ser una ruta absoluta")
    path = Path(raw_path)
    if str(path) != os.path.normpath(raw_path) or path == Path("/"):
        raise ValueError("mount_path no es una ruta canónica válida")
    if path.is_symlink() or not path.is_dir() or path.resolve(strict=True) != path:
        raise ValueError("mount_path debe ser un directorio real y canónico")

    try:
        max_bytes = int(query["max_bytes"])
        min_host_free_bytes = int(query["min_host_free_bytes"])
    except (KeyError, ValueError) as error:
        raise ValueError("los límites de almacenamiento deben ser enteros") from error
    if max_bytes <= 0 or min_host_free_bytes < 0:
        raise ValueError("los límites de almacenamiento no son válidos")

    mount = find_mount(mountinfo, str(path))
    if mount["filesystem"] != "ext4" or not LOOP_DEVICE.fullmatch(mount["source"]):
        raise ValueError("se requiere un montaje ext4 respaldado por loop")
    if "rw" not in mount["mount_options"] and "rw" not in mount["super_options"]:
        raise ValueError("el montaje debe permitir escritura")

    backing_path = Path(backing_file)
    if not backing_path.is_absolute() or backing_path.is_symlink():
        raise ValueError("el archivo de respaldo no es una ruta válida")
    backing_stat = backing_path.stat()
    if not os.path.isfile(backing_path):
        raise ValueError("el respaldo loop no es un archivo regular")
    if backing_stat.st_size <= 0 or backing_stat.st_blocks * 512 < backing_stat.st_size:
        raise ValueError("el archivo de respaldo no está completamente preasignado")

    filesystem = statvfs(str(path))
    filesystem_bytes = filesystem.f_blocks * filesystem.f_frsize
    if filesystem_bytes <= 0 or filesystem_bytes > max_bytes:
        raise ValueError("la capacidad ext4 supera el límite duro solicitado")

    host = statvfs(str(backing_path.parent))
    host_free_bytes = host.f_bavail * host.f_frsize
    if host_free_bytes < min_host_free_bytes:
        raise ValueError("el espacio libre del host está bajo el margen requerido")

    return {
        "verified": "true",
        "mount_path": str(path),
        "filesystem_bytes": str(filesystem_bytes),
        "host_free_bytes": str(host_free_bytes),
    }


def main():
    try:
        query = json.load(sys.stdin)
        raw_path = query.get("mount_path", "")
        if not os.path.isabs(raw_path):
            raise ValueError("mount_path debe ser una ruta absoluta")
        mount = find_mount(Path("/proc/self/mountinfo").read_text(), os.path.normpath(raw_path))
        if not LOOP_DEVICE.fullmatch(mount["source"]):
            raise ValueError("el montaje no está respaldado por un dispositivo loop")
        result = subprocess.run(
            ["losetup", "--noheadings", "--output", "BACK-FILE", "--raw", mount["source"]],
            check=True,
            capture_output=True,
            text=True,
        )
        backing_file = result.stdout.strip()
        if not backing_file:
            raise ValueError("no se pudo identificar el archivo de respaldo loop")
        print(json.dumps(inspect_storage(query, Path("/proc/self/mountinfo").read_text(), backing_file)))
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Preflight de almacenamiento bloqueado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

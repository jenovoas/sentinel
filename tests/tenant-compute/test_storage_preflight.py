import importlib.util
import os
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[2] / "scripts" / "tenant_compute_storage_preflight.py"
SPEC = importlib.util.spec_from_file_location("tenant_compute_storage_preflight", SCRIPT)
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


class FakeStatvfs:
    def __init__(self, total_bytes, free_bytes):
        self.f_blocks = total_bytes // 4096
        self.f_frsize = 4096
        self.f_bavail = free_bytes // 4096


class StoragePreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(__import__("tempfile").TemporaryDirectory()))
        self.mount = self.directory / "tenant-data"
        self.mount.mkdir()
        self.image = self.directory / "tenant.ext4"
        with self.image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 4096)
        self.query = {
            "mount_path": str(self.mount),
            "max_bytes": "1048576",
            "min_host_free_bytes": "4096",
        }
        self.mountinfo = f"36 25 7:7 / {self.mount} rw,relatime - ext4 /dev/loop7 rw\n"

    def inspect(self, *, mountinfo=None, image=None, mount_bytes=524288, host_free=16384):
        return PREFLIGHT.inspect_storage(
            self.query,
            self.mountinfo if mountinfo is None else mountinfo,
            self.image if image is None else image,
            statvfs=lambda path: FakeStatvfs(
                mount_bytes if path == str(self.mount) else 1048576,
                host_free,
            ),
        )

    def test_accepts_preallocated_ext4_loop_mount_below_limit(self):
        result = self.inspect()
        self.assertEqual(result["verified"], "true")
        self.assertEqual(result["filesystem_bytes"], "524288")

    def test_rejects_path_that_is_not_mounted(self):
        with self.assertRaisesRegex(ValueError, "punto de montaje"):
            self.inspect(mountinfo="")

    def test_rejects_ambiguous_stacked_mounts(self):
        with self.assertRaisesRegex(ValueError, "exactamente un punto de montaje"):
            self.inspect(mountinfo=self.mountinfo + self.mountinfo)

    def test_rejects_non_ext4_or_non_loop_mount(self):
        mountinfo = f"36 25 7:7 / {self.mount} rw - xfs /dev/sda1 rw\n"
        with self.assertRaisesRegex(ValueError, "ext4 respaldado por loop"):
            self.inspect(mountinfo=mountinfo)

    def test_rejects_filesystem_larger_than_requested_limit(self):
        with self.assertRaisesRegex(ValueError, "supera el límite duro"):
            self.inspect(mount_bytes=2097152)

    def test_rejects_insufficient_host_free_space(self):
        with self.assertRaisesRegex(ValueError, "margen requerido"):
            self.inspect(host_free=0)

    def test_rejects_sparse_backing_image(self):
        sparse = self.directory / "sparse.ext4"
        with sparse.open("wb") as handle:
            handle.truncate(1048576)
        with self.assertRaisesRegex(ValueError, "completamente preasignado"):
            self.inspect(image=sparse)

    def test_rejects_read_only_mount(self):
        mountinfo = f"36 25 7:7 / {self.mount} ro - ext4 /dev/loop7 ro\n"
        with self.assertRaisesRegex(ValueError, "permitir escritura"):
            self.inspect(mountinfo=mountinfo)


if __name__ == "__main__":
    unittest.main()

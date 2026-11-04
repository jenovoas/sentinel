import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "tenant_compute_storage_provision.py"
SPEC = importlib.util.spec_from_file_location("tenant_compute_storage_provision", SCRIPT)
PROVISION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROVISION
SPEC.loader.exec_module(PROVISION)


class FakeStatvfs:
    f_blocks = 128
    f_bavail = 4096
    f_frsize = 4096


class ProvisionerTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.paths = PROVISION.StoragePaths(
            image_root=self.directory / "images",
            mount_root=self.directory / "mounts",
            unit_root=self.directory / "units",
        )
        self.commands = []

    def run_command(self, args):
        self.commands.append(args)
        if args[0] == "fallocate":
            with open(args[-1], "r+b") as handle:
                os.posix_fallocate(handle.fileno(), 0, int(args[2]))
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[0] == "systemd-escape":
            return subprocess.CompletedProcess(args, 0, "srv-sentinel-tenants-laespiguita.mount\n", "")
        if args[0] == "blkid":
            return subprocess.CompletedProcess(args, 0, "ext4\n", "")
        if args[0] == "losetup":
            return subprocess.CompletedProcess(args, 0, f"{self.paths.image_root / 'laespiguita.ext4'}\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")

    def statvfs(self, path):
        return FakeStatvfs()

    def provision(self, **overrides):
        options = {
            "tenant_id": "laespiguita",
            "size_bytes": 1024 * 1024,
            "min_host_free_bytes": 4096,
            "paths": self.paths,
            "run_command": self.run_command,
            "statvfs": self.statvfs,
            "mountinfo": "",
        }
        options.update(overrides)
        return PROVISION.provision_storage(**options)

    def test_creates_preallocated_ext4_image_and_persistent_unit(self):
        result = self.provision()
        image = Path(result["image_path"])
        unit = self.paths.unit_root / result["unit_name"]

        self.assertTrue(image.is_file())
        self.assertEqual(image.stat().st_size, 1024 * 1024)
        self.assertGreaterEqual(image.stat().st_blocks * 512, image.stat().st_size)
        mkfs_command = next(args for args in self.commands if args[0] == "mkfs.ext4")
        fallocate_positions = [index for index, args in enumerate(self.commands) if args[0] == "fallocate"]
        self.assertIn("nodiscard", mkfs_command)
        self.assertEqual(len(fallocate_positions), 2)
        self.assertGreater(fallocate_positions[1], self.commands.index(mkfs_command))
        self.assertEqual(unit.stat().st_mode & 0o777, 0o644)
        self.assertIn("Options=loop,nodev,nosuid", unit.read_text())
        self.assertIn(["systemctl", "enable", "--now", result["unit_name"]], self.commands)
        self.assertEqual(result["verified"], "false")
        self.assertEqual(result["status"], "mount_requested")

    def test_generated_mount_unit_passes_systemd_analyze(self):
        systemd_analyze = shutil.which("systemd-analyze")
        if systemd_analyze is None:
            self.skipTest("systemd-analyze no está instalado")

        image_path, mount_path = PROVISION.target_paths("laespiguita", self.paths)
        unit_name, content = PROVISION.render_mount_unit(
            image_path,
            mount_path,
            "laespiguita",
            lambda args: subprocess.run(args, check=True, capture_output=True, text=True),
        )
        unit_path = self.paths.unit_root / unit_name
        PROVISION.write_unit(unit_path, content)

        result = subprocess.run([systemd_analyze, "verify", str(unit_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repeated_provisioning_reuses_matching_image_and_unit(self):
        first = self.provision()
        self.commands.clear()
        second = self.provision()

        self.assertEqual(first["image_path"], second["image_path"])
        self.assertEqual(second["image_created"], "false")
        self.assertEqual(second["unit_created"], "false")
        self.assertFalse(any(args[0] in {"fallocate", "mkfs.ext4"} for args in self.commands))

    def test_rejects_invalid_tenant_before_creating_paths(self):
        with self.assertRaisesRegex(ValueError, "tenant_id"):
            self.provision(tenant_id="../laespiguita")
        self.assertFalse(self.paths.image_root.exists())

    def test_rejects_world_writable_storage_root(self):
        self.paths.image_root.mkdir(mode=0o750)
        self.paths.image_root.chmod(0o777)

        with self.assertRaisesRegex(ValueError, "escribible por grupo/otros"):
            self.provision()
        self.assertFalse(any(args[0] == "mkfs.ext4" for args in self.commands))

    def test_rejects_size_not_aligned_to_ext4_block_size(self):
        with self.assertRaisesRegex(ValueError, "múltiplo de 4096"):
            self.provision(size_bytes=4097)
        self.assertFalse(self.paths.image_root.exists())

    def test_rejects_insufficient_host_free_space(self):
        with self.assertRaisesRegex(ValueError, "espacio libre"):
            self.provision(min_host_free_bytes=4096 * 4096)
        self.assertFalse(any(args[0] == "mkfs.ext4" for args in self.commands))

    def test_rejects_group_or_world_accessible_existing_image(self):
        self.paths.image_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        with image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 1024 * 1024)
        image.chmod(0o666)

        with self.assertRaisesRegex(ValueError, "no ser accesible por grupo/otros"):
            self.provision()
        self.assertFalse(any(args[0] == "systemctl" for args in self.commands))

    def test_rejects_existing_image_with_wrong_size(self):
        self.paths.image_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        image.write_bytes(b"x")
        image.chmod(0o600)

        with self.assertRaisesRegex(ValueError, "tamaño distinto"):
            self.provision()
        self.assertFalse(any(args[0] == "mkfs.ext4" for args in self.commands))

    def test_rejects_sparse_existing_image(self):
        self.paths.image_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        with image.open("wb") as handle:
            handle.truncate(1024 * 1024)
        image.chmod(0o600)

        with self.assertRaisesRegex(ValueError, "completamente preasignada"):
            self.provision()
        self.assertFalse(any(args[0] == "blkid" for args in self.commands))

    def test_rejects_existing_non_ext4_image(self):
        self.paths.image_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        with image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 1024 * 1024)
        image.chmod(0o600)
        original_run_command = self.run_command
        self.run_command = lambda args: subprocess.CompletedProcess(args, 0, "xfs\n", "") if args[0] == "blkid" else original_run_command(args)

        with self.assertRaisesRegex(ValueError, "no contiene.*ext4"):
            self.provision()

    def test_refuses_nonempty_unmounted_mountpoint_before_allocating_image(self):
        self.paths.mount_root.mkdir(mode=0o750)
        mount_path = self.paths.mount_root / "laespiguita"
        mount_path.mkdir()
        (mount_path / "keep.txt").write_text("preserve")

        with self.assertRaisesRegex(ValueError, "debe estar vacío"):
            self.provision()
        self.assertFalse((self.paths.image_root / "laespiguita.ext4").exists())
        self.assertEqual((mount_path / "keep.txt").read_text(), "preserve")

    def test_refuses_conflicting_systemd_unit_before_allocating_image(self):
        self.paths.unit_root.mkdir(mode=0o755)
        conflicting_unit = self.paths.unit_root / "srv-sentinel-tenants-laespiguita.mount"
        conflicting_unit.write_text("foreign unit")
        conflicting_unit.chmod(0o644)

        with self.assertRaisesRegex(ValueError, "unidad systemd distinta"):
            self.provision()
        self.assertFalse((self.paths.image_root / "laespiguita.ext4").exists())

    def test_rejects_writable_existing_systemd_unit_before_allocating_image(self):
        self.paths.unit_root.mkdir(mode=0o755)
        image_path, mount_path = PROVISION.target_paths("laespiguita", self.paths)
        unit_name, content = PROVISION.render_mount_unit(image_path, mount_path, "laespiguita", self.run_command)
        unit_path = self.paths.unit_root / unit_name
        unit_path.write_text(content)
        unit_path.chmod(0o666)

        with self.assertRaisesRegex(ValueError, "unidad systemd debe pertenecer"):
            self.provision()
        self.assertFalse((self.paths.image_root / "laespiguita.ext4").exists())
        self.assertFalse(any(args[0] == "systemctl" for args in self.commands))

    def test_active_mount_is_verified_and_made_persistent(self):
        self.paths.image_root.mkdir(mode=0o750)
        self.paths.mount_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        with image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 1024 * 1024)
        image.chmod(0o600)
        mount_path = self.paths.mount_root / "laespiguita"
        mount_path.mkdir()
        mountinfo = f"36 25 7:7 / {mount_path} rw,relatime - ext4 /dev/loop7 rw\n"

        result = self.provision(mountinfo=mountinfo)

        self.assertEqual(result["verified"], "true")
        self.assertEqual(result["status"], "verified_and_persistent")
        self.assertTrue((self.paths.unit_root / result["unit_name"]).is_file())
        self.assertIn(["systemctl", "enable", "--now", result["unit_name"]], self.commands)

    def test_active_mount_with_different_backing_image_is_rejected(self):
        self.paths.image_root.mkdir(mode=0o750)
        image = self.paths.image_root / "laespiguita.ext4"
        with image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 1024 * 1024)
        image.chmod(0o600)
        other_image = self.directory / "other.ext4"
        with other_image.open("wb") as handle:
            os.posix_fallocate(handle.fileno(), 0, 1024 * 1024)
        original_run_command = self.run_command

        def mismatched_loop(args):
            if args[0] == "losetup":
                return subprocess.CompletedProcess(args, 0, f"{other_image}\n", "")
            return original_run_command(args)

        self.run_command = mismatched_loop
        self.paths.mount_root.mkdir(mode=0o750)
        mount_path = self.paths.mount_root / "laespiguita"
        mount_path.mkdir()
        mountinfo = f"36 25 7:7 / {mount_path} rw,relatime - ext4 /dev/loop7 rw\n"

        with self.assertRaisesRegex(ValueError, "no corresponde a la imagen"):
            self.provision(mountinfo=mountinfo)
        self.assertFalse((self.paths.unit_root / "srv-sentinel-tenants-laespiguita.mount").exists())


if __name__ == "__main__":
    unittest.main()

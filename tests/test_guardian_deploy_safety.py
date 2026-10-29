from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GuardianDeploySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = (ROOT / "ebpf/guardian_cognitive.c").read_text()
        cls.bootstrap = (ROOT / "scripts/bootstrap-sentinel-ebpf.sh").read_text()
        cls.mode = (ROOT / "scripts/sentinel-guardian-mode.sh").read_text()
        cls.rollback = (ROOT / "scripts/sentinel-guardian-rollback.sh").read_text()
        cls.installer = (ROOT / "scripts/install-sentinel-ebpf.sh").read_text()
        cls.packager = (ROOT / "scripts/package-sentinel-ebpf.sh").read_text()
        cls.unit = (ROOT / "systemd/sentinel-ebpf.service").read_text()

    def test_missing_mode_map_entry_is_fail_open(self):
        audit_gate = "if (!mode || *mode == 0)"
        self.assertIn("guardian_mode_map SEC(\".maps\")", self.program)
        self.assertIn(audit_gate, self.program)
        audit_start = self.program.index(audit_gate)
        audit_end = self.program.index("return 0;", audit_start)
        first_deny = self.program.index("return -EACCES;")
        self.assertLess(audit_end, first_deny)

    def test_bootstrap_populates_and_checks_map_before_attach(self):
        batch = self.bootstrap.index('bpftool batch file "$BATCH_FILE"')
        map_count = self.bootstrap.index('map_entries=$(bpftool map dump pinned "$MAP_PIN"')
        required_path_check = self.bootstrap.index('for tool in bash sh sudo systemctl rm bpftool sshd; do')
        attach = self.bootstrap.index('"$ATTACHER" "$PROGRAM_PIN" "$LINK_PIN"')
        self.assertLess(batch, map_count)
        self.assertLess(map_count, required_path_check)
        self.assertLess(required_path_check, attach)
        self.assertIn("refusing to attach with an empty executable inventory", self.bootstrap)
        self.assertIn("required command is not whitelisted", self.bootstrap)

    def test_bootstrap_attaches_in_audit_mode(self):
        audit_update = 'bpftool map update pinned "$MODE_PIN" key hex 00 00 00 00 value hex 00 00 00 00 any'
        self.assertIn(audit_update, self.bootstrap)
        self.assertLess(self.bootstrap.index(audit_update), self.bootstrap.index('"$ATTACHER"'))
        self.assertIn("Guardian attached in audit-only mode", self.bootstrap)

    def test_enforcement_arms_rollback_before_setting_enforce(self):
        timer = "systemd-run --quiet --unit=sentinel-guardian-auto-rollback"
        enforce = 'value hex 01 00 00 00 any'
        self.assertLess(self.mode.index(timer), self.mode.index(enforce))
        self.assertIn("automatic rollback timer did not become active", self.mode)
        self.assertIn('lookup_path "$ROLLBACK_HELPER"', self.mode)
        self.assertIn('echo "Guardian is in audit-only mode."', self.mode)

    def test_service_stop_detaches_and_rollback_falls_back_to_detach(self):
        self.assertIn("ExecStop=/usr/local/libexec/sentinel-guardian-rollback --detach", self.unit)
        mode_reset = 'value hex 00 00 00 00 any'
        detach = 'rm -f "$LINK_PIN"'
        self.assertIn(mode_reset, self.rollback)
        self.assertIn(detach, self.rollback)
        self.assertIn('rm -f "$PROGRAM_PIN" "$WHITELIST_PIN" "$MODE_PIN" "$EVENTS_PIN"', self.rollback)

    def test_installer_stages_all_helpers_without_starting_production_service(self):
        self.assertIn('"$BUNDLE_DIR/sentinel-guardian-mode.sh"', self.installer)
        self.assertIn('"$BUNDLE_DIR/sentinel-guardian-rollback.sh"', self.installer)
        self.assertIn('"$BUNDLE_DIR/sentinel-ebpf.service"', self.installer)
        self.assertIn("systemctl daemon-reload", self.installer)
        self.assertNotIn("systemctl enable", self.installer)
        self.assertNotIn("systemctl start", self.installer)

    def test_package_contains_a_buildable_object_and_install_path(self):
        self.assertIn('OBJECT="$STAGE/guardian_cognitive.o"', self.packager)
        self.assertIn('"$REPO_DIR/scripts/install-sentinel-ebpf.sh"', self.packager)
        self.assertIn('"$REPO_DIR/systemd/sentinel-ebpf.service"', self.packager)


if __name__ == "__main__":
    unittest.main()

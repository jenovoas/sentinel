"""Non-production unit checks; run explicitly with unittest, never against live DBs."""
import importlib.util
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location('sentinel_recovery',
                                             Path(__file__).parents[1] / 'recovery.py')
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)


class RecoveryHelpersTest(unittest.TestCase):

    def test_failed_command_does_not_expose_output(self):
        with self.assertRaisesRegex(RuntimeError, 'output withheld') as error:
            recovery.run([sys.executable, '-c',
                          'import sys; print("private-row", file=sys.stderr); sys.exit(4)'])
        self.assertNotIn('private-row', str(error.exception))


if __name__ == '__main__':
    unittest.main()

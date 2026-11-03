"""CLI checks that do not require Docker or modify a lab."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
SCRIPTS = ('setup_frr_container.sh', 'setup_frr_coverage.sh',
           'setup_frr_legacy.sh', 'collect_c_coverage.sh')


class ScriptTests(unittest.TestCase):
    def test_help_from_another_directory(self):
        for name in SCRIPTS:
            with self.subTest(script=name):
                result = subprocess.run(['bash', str(BASE / name), '--help'], cwd='/tmp',
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('--container', result.stdout)
                self.assertIn('--port', result.stdout)

    def test_bad_options_fail_before_docker(self):
        for name in SCRIPTS:
            for options in (['--unknown'], ['--port'], ['--port', '0'], ['--port', '65536']):
                with self.subTest(script=name, options=options):
                    result = subprocess.run(['bash', str(BASE / name), *options], cwd='/tmp',
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertTrue(result.stderr.startswith('error:'), result.stderr)

    def test_existing_lab_is_not_replaced_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / 'calls.txt'
            docker = root / 'docker'
            docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$SCRIPT_TEST_LOG"\nexit 0\n')
            docker.chmod(0o755)
            env = {**os.environ, 'PATH': f"{root}:{os.environ['PATH']}", 'SCRIPT_TEST_LOG': str(log)}
            result = subprocess.run(['bash', str(BASE / 'setup_frr_container.sh')],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('already exists', result.stderr)
            self.assertEqual(log.read_text().splitlines(), ['info', 'container inspect frr-lab'])


if __name__ == '__main__':
    unittest.main()

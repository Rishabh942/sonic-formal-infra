"""Shared FRR observations for a host Docker client or an in-container runner."""

import json
from pathlib import Path
import subprocess


class FrrBackend:
    def __init__(self, local=False, container='frr-lab', log_path='/tmp/bgpd.log'):
        self.local = local
        self.container = container
        self.log_path = log_path

    def command(self, *args):
        command = list(args) if self.local else ['docker', 'exec', self.container, *args]
        return subprocess.check_output(command, stderr=subprocess.PIPE, timeout=5)

    def paths(self, prefix):
        output = self.command('vtysh', '-c', f'show bgp ipv4 unicast {prefix} json')
        try:
            data = json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f'non-JSON RIB response: {output!r}') from exc
        if not isinstance(data, dict) or (data and 'paths' not in data):
            raise ValueError(f'unexpected RIB response: {data!r}')
        paths = data.get('paths', [])
        if not isinstance(paths, list):
            raise ValueError('RIB paths must be a list')
        return paths

    def log(self):
        try:
            return self.command('cat', self.log_path).decode(errors='replace')[-24000:]
        except (OSError, subprocess.SubprocessError):
            return ''

    def clear_log(self):
        if self.local:
            Path(self.log_path).write_text('')
        else:
            self.command('truncate', '-s', '0', self.log_path)


FRR = FrrBackend()


def configure(local=False, container='frr-lab', log_path='/tmp/bgpd.log'):
    # Retain object identity for modules importing the shared backend.
    FRR.local, FRR.container, FRR.log_path = local, container, log_path

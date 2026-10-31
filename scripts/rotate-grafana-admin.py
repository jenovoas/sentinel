#!/usr/bin/env python3
"""Run as root on Marte: rotate persisted Grafana admin and use a mounted secret."""
import base64
import datetime
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import yaml

COMPOSE = Path('/opt/sentinel-marte/compose.yaml')
SECRET = Path('/etc/sentinel/grafana-admin-password')
CONTAINER = 'sentinel-marte-grafana'


def run(args, data=None):
    result = subprocess.run(args, input=data, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Subprocess failed; sensitive output withheld')
    return result.stdout


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Run with sudo -n')
    if SECRET.exists():
        raise RuntimeError('Secret already exists; inspect prior rotation before rerunning')
    config = yaml.safe_load(COMPOSE.read_text())
    grafana = config['services']['grafana']
    environment = grafana['environment']
    if 'GF_SECURITY_ADMIN_PASSWORD' not in environment:
        raise RuntimeError('Unexpected Grafana credential configuration')
    uid = int(run(['docker', 'exec', CONTAINER, 'id', '-u']).strip())
    gid = int(run(['docker', 'exec', CONTAINER, 'id', '-g']).strip())
    password = secrets.token_hex(32)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = str(COMPOSE) + '.pre-secret-rotation-' + stamp
    shutil.copy2(COMPOSE, backup)
    os.chmod(backup, 0o600)
    environment.pop('GF_SECURITY_ADMIN_PASSWORD')
    environment['GF_SECURITY_ADMIN_PASSWORD__FILE'] = '/run/secrets/grafana-admin-password'
    grafana.setdefault('volumes', []).append(str(SECRET) + ':/run/secrets/grafana-admin-password:ro')
    SECRET.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(SECRET, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    with os.fdopen(fd, 'w') as stream:
        stream.write(password + '\n'); stream.flush(); os.fsync(stream.fileno())
    os.chown(SECRET, uid, gid)
    fd, staged_name = tempfile.mkstemp(prefix='.grafana-compose-', suffix='.yaml', dir=COMPOSE.parent)
    staged = Path(staged_name)
    try:
        with os.fdopen(fd, 'w') as stream:
            yaml.safe_dump(config, stream, sort_keys=False)
        run(['docker', 'compose', '--project-directory', str(COMPOSE.parent), '-f', str(staged), 'config', '--quiet'])
        run(['docker', 'exec', '-i', CONTAINER, 'grafana', 'cli', 'admin', 'reset-admin-password', '--password-from-stdin'], password + '\n')
        os.chmod(staged, 0o644)
        os.replace(staged, COMPOSE)
        run(['docker', 'compose', '-f', str(COMPOSE), 'up', '-d', '--no-build', '--no-deps', 'grafana'])
        auth = base64.b64encode(('admin:' + password).encode()).decode()
        for attempt in range(30):
            try:
                request = urllib.request.Request('http://10.88.0.6:3000/api/user', headers={'Authorization': 'Basic ' + auth})
                with urllib.request.urlopen(request, timeout=5) as response:
                    identity = json.load(response)
                if identity.get('isGrafanaAdmin') is not True:
                    raise RuntimeError('New credential did not authenticate a Grafana administrator')
                print('Grafana new credential authenticated administrator; password supplied by protected file')
                print('Protected Compose backup:', backup)
                return
            except (OSError, ValueError):
                time.sleep(2)
        raise RuntimeError('Grafana did not confirm new administrator credential')
    finally:
        staged.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Grafana rotation stopped:', type(error).__name__, str(error), file=sys.stderr)
        print('Inspect protected backups and secret; do not rerun blindly.', file=sys.stderr)
        sys.exit(1)

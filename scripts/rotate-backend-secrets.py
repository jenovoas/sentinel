#!/usr/bin/env python3
"""Rotate backend credentials without placing values in argv or tool output.

Run as root on Fenix. Existing images and private configuration are preserved.
A failure leaves protected backups for recovery; never blindly rerun after failure.
"""
import datetime
import grp
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit, urlunsplit, quote

ROOT = Path(__file__).resolve().parent.parent
TARGET = Path('/etc/sentinel/backend.env')
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
COMPOSE = ['docker', 'compose', '--env-file', str(TARGET), '-f', str(ROOT / 'docker-compose.fenix.yml')]


def run(args, data=None):
    if args[0] == 'ssh':
        operator = os.environ.get('SUDO_USER')
        if not operator or operator == 'root':
            raise RuntimeError('Run through sudo -n from the configured SSH operator')
        args = ['runuser', '-u', operator, '--'] + args
    result = subprocess.run(args, input=data, text=True, capture_output=True)
    if result.returncode:
        # Do not include argv, stdout or stderr: any may contain credentials.
        raise RuntimeError('Operation failed; sensitive subprocess output withheld')
    return result.stdout


def replace_password(url, password):
    parsed = urlsplit(url)
    if not parsed.hostname or parsed.password is None:
        raise ValueError('Expected authenticated connection URL')
    host = '[' + parsed.hostname + ']' if ':' in parsed.hostname else parsed.hostname
    netloc = quote(parsed.username or '', safe='') + ':' + quote(password, safe='') + '@' + host
    if parsed.port:
        netloc += ':' + str(parsed.port)
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def stage_env(changes):
    rows = TARGET.read_text().splitlines()
    seen = set()
    output = []
    for row in rows:
        key, sep, _ = row.partition('=')
        if sep and key in changes:
            if key in seen:
                raise ValueError('Duplicate credential key; original preserved')
            seen.add(key)
            row = key + '=' + changes[key]
        output.append(row)
    output.extend(key + '=' + value for key, value in changes.items() if key not in seen)
    fd, name = tempfile.mkstemp(prefix='.rotate-', dir=TARGET.parent)
    with os.fdopen(fd, 'w') as stream:
        stream.write('\n'.join(output) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.chown(name, 0, grp.getgrnam('docker').gr_gid)
    os.chmod(name, 0o640)
    return Path(name)


# The receiver reads the new token on stdin; neither shell argv nor output has it.
REMOTE_TOKEN_UPDATE = r'''
import datetime,os,pathlib,shutil,sys,tempfile
p=pathlib.Path('/etc/sentinel/security-gateway.env')
token=sys.stdin.readline().strip()
if len(token)!=64 or any(c not in '0123456789abcdef' for c in token):
 raise RuntimeError('Invalid token input')
rows=p.read_text().splitlines(); key='SENTINEL_TELEMETRY_TOKEN'; seen=0; out=[]
for row in rows:
 if row.startswith(key+'='):
  seen+=1; row=key+'='+token
 out.append(row)
if seen!=1: raise RuntimeError('Expected exactly one telemetry token')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=str(p)+'.pre-secret-rotation-'+stamp
shutil.copy2(p,backup); os.chmod(backup,0o600)
fd,name=tempfile.mkstemp(dir=p.parent,prefix='.gateway-token-')
with os.fdopen(fd,'w') as f:
 f.write('\n'.join(out)+'\n'); f.flush(); os.fsync(f.fileno())
os.chmod(name,0o600); os.replace(name,p)
print('Protected gateway configuration updated; backup created')
'''


def main():
    if os.geteuid() != 0:
        raise RuntimeError('Run using sudo -n')
    config = json.loads(run(COMPOSE + ['config', '--format', 'json']))
    environment = config['services']['backend']['environment']
    for service in ('sentinel-backend', 'sentinel-cortex', 'sentinel-postgres', 'sentinel-redis'):
        if run(['docker', 'inspect', '--format', '{{.State.Health.Status}}', service]).strip() != 'healthy':
            raise RuntimeError('Required service is not healthy; no rotation performed')
    run(['ssh', '-p', '4222', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'marte',
         'sudo -n test -r /etc/sentinel/security-gateway.env && systemctl is-active sentinel-security-gateway'])
    new_pg, new_redis, new_jwt, new_token, reserved_grafana = [secrets.token_hex(32) for _ in range(5)]
    changes = {
        'POSTGRES_PASSWORD': new_pg, 'REDIS_PASSWORD': new_redis,
        'SECRET_KEY': new_jwt, 'INTERNAL_TELEMETRY_TOKEN': new_token,
        'SENTINEL_REDIS_URL': replace_password(environment['SENTINEL_REDIS_URL'], new_redis),
        'GF_ADMIN_PASSWORD': reserved_grafana,
    }
    # Update optional aliases only if present; derived Compose URLs use the new stores.
    present = {row.partition('=')[0] for row in TARGET.read_text().splitlines() if '=' in row}
    if 'SENTINEL_JWT_SECRET' in present:
        changes['SENTINEL_JWT_SECRET'] = new_jwt
    if 'REDIS_URL' in present:
        changes['REDIS_URL'] = replace_password(environment['SENTINEL_REDIS_URL'], new_redis)
    if 'DATABASE_URL' in present:
        changes['DATABASE_URL'] = replace_password(environment['DATABASE_URL'], new_pg)
    staged = stage_env(changes)
    try:
        staged_compose = COMPOSE.copy()
        staged_compose[staged_compose.index(str(TARGET))] = str(staged)
        run(staged_compose + ['config', '--quiet'])
        backup = str(TARGET) + '.pre-secret-rotation-' + STAMP
        shutil.copy2(TARGET, backup)
        os.chmod(backup, 0o600)
        print('Protected backend backup:', backup, flush=True)
        role = config['services']['postgres']['environment']['POSTGRES_USER']
        database = config['services']['postgres']['environment']['POSTGRES_DB']
        # Role and generated password never enter process argv.
        sql = 'ALTER ROLE "' + role.replace('"', '""') + '" PASSWORD \'' + new_pg + "';\n"
        run(['docker', 'exec', '-i', 'sentinel-postgres', 'psql', '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-U', role, '-d', database], sql)
        result = run(['docker', 'exec', '-i', 'sentinel-redis', 'sh', '-c',
                      'REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -x CONFIG SET requirepass'], new_redis)
        if result.strip() != 'OK':
            raise RuntimeError('Redis did not acknowledge rotation')
        os.replace(staged, TARGET)
        import shlex
        command = 'sudo -n python3 -c ' + shlex.quote(REMOTE_TOKEN_UPDATE)
        run(['ssh', '-p', '4222', '-o', 'BatchMode=yes', 'marte', command], new_token + '\n')
        print('Store credentials and configurations rotated; applying dependent services', flush=True)
        run(COMPOSE + ['up', '-d', '--no-build', '--no-deps', '--wait', '--wait-timeout', '120', 'redis', 'backend', 'cortex'])
        run(['ssh', '-p', '4222', '-o', 'BatchMode=yes', 'marte',
             'sudo -n systemctl restart sentinel-security-gateway && systemctl is-active sentinel-security-gateway'])
        print('Backend/Redis/Cortex healthy; gateway active. JWT sessions invalidated.', flush=True)
        print('GF_ADMIN_PASSWORD in Fenix rotated; live Marte Grafana requires separate CLI/store rotation.', flush=True)
    finally:
        staged.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Rotation stopped:', type(error).__name__, str(error), file=sys.stderr)
        print('Do not rerun blindly. Check service state and protected backups.', file=sys.stderr)
        sys.exit(1)

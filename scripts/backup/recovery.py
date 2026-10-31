#!/usr/bin/env python3
"""Backup, protected SSH round-trip and isolated restore; never touch live volumes."""
import argparse
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import shutil
import subprocess
import tempfile
import time


# Only aggregate fingerprints leave PostgreSQL. No customer rows are logged.
CATALOG_SQL = r"""
SELECT json_build_array('columns', table_schema, table_name, column_name,
 ordinal_position, data_type, udt_name, is_nullable, column_default)::text
 FROM information_schema.columns
 WHERE table_schema NOT IN ('pg_catalog','information_schema')
 ORDER BY table_schema, table_name, ordinal_position;
SELECT json_build_array('constraint', n.nspname,c.relname,k.conname,
 pg_get_constraintdef(k.oid),k.convalidated)::text
 FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
 JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname NOT LIKE 'pg_%' ORDER BY n.nspname,c.relname,k.conname;
SELECT json_build_array('index',schemaname,tablename,indexname,indexdef)::text
 FROM pg_indexes WHERE schemaname NOT LIKE 'pg_%'
 ORDER BY schemaname,tablename,indexname;
SELECT json_build_array('view',schemaname,viewname,definition)::text
 FROM pg_views WHERE schemaname NOT LIKE 'pg_%'
 AND schemaname <> 'information_schema' ORDER BY schemaname,viewname;
SELECT json_build_array('extension',extname,extversion)::text
 FROM pg_extension ORDER BY extname;
SELECT format($sql$SELECT json_build_array('table',%L,count(*),
 encode(sha256(convert_to(coalesce(string_agg(
 encode(sha256(convert_to(row_to_json(t)::text,'UTF8')),'hex'),''
 ORDER BY encode(sha256(convert_to(row_to_json(t)::text,'UTF8')),'hex')),''),
 'UTF8')),'hex'))::text FROM %I.%I t;$sql$,
 schemaname||'.'||tablename,schemaname,tablename)
 FROM pg_tables WHERE schemaname NOT LIKE 'pg_%'
 AND schemaname <> 'information_schema' ORDER BY schemaname,tablename
\gexec
SELECT json_build_array('large_objects',count(*),
 encode(sha256(convert_to(coalesce(string_agg(
 loid::text||':'||pageno::text||':'||encode(sha256(data),'hex'),''
 ORDER BY loid,pageno),''),'UTF8')),'hex'))::text
 FROM pg_largeobject;
"""


def run(args, *, data=None, env=None):
    # stderr is captured, not echoed: SQL/restore errors can include customer data.
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    if result.returncode:
        raise RuntimeError(f"{Path(args[0]).name} failed (exit {result.returncode}); output withheld")
    return result.stdout


def psql(container, user, database):
    return ['docker', 'exec', '-i', container, 'psql', '-X', '-qAt',
            '-v', 'ON_ERROR_STOP=1', '-U', user, '-d', database]


def sql(container, user, database, statement):
    return run(psql(container, user, database), data=statement.encode()).decode().strip()


def fingerprint(container, user, database, snapshot=None):
    begin = 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\n'
    if snapshot:
        begin += f"SET TRANSACTION SNAPSHOT '{snapshot}';\n"
    values = sql(container, user, database, begin + CATALOG_SQL + '\nROLLBACK;\n')
    records = [json.loads(line) for line in values.splitlines()]
    return records


def sha256(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def recover(config):
    os.umask(0o077)
    start = time.monotonic()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    directory = Path(config['backup_dir']).resolve(strict=True)
    if directory.stat().st_mode & 0o077:
        raise RuntimeError('backup_dir must be private (0700)')
    container, user, database = (config[k] for k in ('container', 'user', 'database'))
    remote = config['remote_dir']
    host = config['ssh_host']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', host) or not re.fullmatch(r'/[A-Za-z0-9_./-]+', remote):
        raise RuntimeError('invalid SSH destination')
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', host]
    lock = (directory / '.recovery.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    db_size = int(sql(container, user, database, 'SELECT pg_database_size(current_database());'))
    # Leave headroom for bootstrap, index rebuilds and PostgreSQL working memory.
    # Refuse before dumping/transferring if this isolated sandbox cannot fit.
    if db_size * 2 + 128 * 1024 * 1024 > 512 * 1024 * 1024:
        raise RuntimeError('database exceeds isolated restore budget; review tmpfs/memory limits')
    required = max(db_size * 4, 256 * 1024 * 1024)
    if shutil.disk_usage(directory).free < required:
        raise RuntimeError('insufficient local backup capacity')
    image = run(['docker', 'inspect', '--format', '{{.Image}}', container]).decode().strip()
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', image):
        raise RuntimeError('source image must resolve to immutable local image ID')
    remote_preflight = """import json,os,shutil,sys
p=sys.argv[1]
os.makedirs(p,mode=0o700,exist_ok=True)
s=os.stat(p)
assert s.st_uid==os.getuid() and not s.st_mode & 0o077
print(json.dumps({'free_bytes':shutil.disk_usage(p).free,'mode':oct(s.st_mode & 0o777)}))
"""
    preflight = json.loads(run(ssh + ['python3 -c ' + shlex.quote(remote_preflight) + ' ' + shlex.quote(remote)]))
    if preflight['free_bytes'] < required:
        raise RuntimeError('insufficient off-node backup capacity')
    restore_name = 'sentinel-recovery-isolated-' + secrets.token_hex(8)
    temporary_created = False
    keeper = None
    evidence = {'started_utc': started, 'source_container': container,
                'source_image': image, 'database_bytes': db_size,
                'local_free_bytes': shutil.disk_usage(directory).free,
                'remote_free_bytes': preflight['free_bytes'], 'remote_mode': preflight['mode'],
                'ssh_host': host, 'remote_dir': remote, 'restore_container': restore_name}
    try:
        keeper = subprocess.Popen(psql(container, user, database), stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        keeper.stdin.write(b'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\nSELECT pg_export_snapshot();\n')
        keeper.stdin.flush()
        snapshot = keeper.stdout.readline().decode().strip()
        if not re.fullmatch(r'[0-9A-Fa-f]+-[0-9A-Fa-f]+-[0-9]+', snapshot):
            raise RuntimeError('could not export source snapshot')
        reference = fingerprint(container, user, database, snapshot)
        before = set(directory.glob('sentinel_backup_*.sql.gz'))
        environment = dict(os.environ, POSTGRES_CONTAINER=container, POSTGRES_USER=user,
                           POSTGRES_DB=database, POSTGRES_SNAPSHOT=snapshot,
                           BACKUP_DIR=str(directory), BACKUP_ENV_FILE='/dev/null',
                           BACKUP_CLEANUP_ENABLED='false', ENCRYPT_ENABLED='false',
                           S3_ENABLED='false', MINIO_ENABLED='false', WEBHOOK_ENABLED='false',
                           WEBHOOK_URL='', LOG_TO_FILE='false', LOG_TO_STDOUT='false')
        backup_start = time.monotonic()
        run(['bash', str(Path(__file__).with_name('backup.sh'))], env=environment)
        candidates = set(directory.glob('sentinel_backup_*.sql.gz')) - before
        if len(candidates) != 1:
            raise RuntimeError('backup did not create exactly one archive')
        archive = candidates.pop()
        evidence['backup_seconds'] = round(time.monotonic() - backup_start, 3)
        keeper.stdin.write(b'ROLLBACK;\n\\q\n')
        keeper.stdin.flush()
        keeper.communicate(timeout=15)
        if keeper.returncode:
            raise RuntimeError('source snapshot session failed')
        keeper = None
        checksum = sha256(archive)
        evidence.update(archive=archive.name, archive_bytes=archive.stat().st_size, sha256=checksum)
        manifest = archive.with_name(archive.name + '.invariants.json')
        manifest.write_text(json.dumps(reference, sort_keys=True) + '\n')
        transfer_start = time.monotonic()
        rsync = ['rsync', '--chmod=F600,D700', '-e',
                 'ssh -o BatchMode=yes -o ConnectTimeout=15']
        run(rsync + [str(archive), str(archive) + '.sha256', str(manifest), host + ':' + remote + '/'])
        remote_hash = run(ssh + ['sha256sum ' + shlex.quote(remote + '/' + archive.name)]).decode().split()[0]
        if remote_hash != checksum:
            raise RuntimeError('off-node checksum mismatch')
        evidence['transfer_seconds'] = round(time.monotonic() - transfer_start, 3)
        with tempfile.TemporaryDirectory(prefix='restore-roundtrip-', dir=directory) as temp:
            received = Path(temp) / archive.name
            received_manifest = Path(temp) / manifest.name
            run(rsync + [host + ':' + remote + '/' + archive.name, str(received)])
            run(rsync + [host + ':' + remote + '/' + manifest.name, str(received_manifest)])
            if sha256(received) != checksum or received_manifest.read_bytes() != manifest.read_bytes():
                raise RuntimeError('received off-node archive or manifest mismatch')
            restore_start = time.monotonic()
            # Scratch data is a container-private tmpfs. No named/live volume, no published port.
            run(['docker', 'run', '-d', '--pull=never', '--name', restore_name,
                 '--label', 'sentinel.recovery.temporary=true', '--network=none',
                 '--memory=512m', '--cpus=1', '--tmpfs',
                 '/var/lib/postgresql/data:rw,nosuid,nodev,size=536870912',
                 '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', '-e', 'POSTGRES_DB=recovery',
                 image])
            temporary_created = True
            for _ in range(60):
                # pg_isready alone can succeed against entrypoint's temporary bootstrap server.
                status = subprocess.run(['docker', 'exec', restore_name, 'sh', '-c',
                                         'test "$(cat /proc/1/comm)" = postgres && '
                                         'pg_isready -U postgres -d recovery'],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if status.returncode == 0:
                    break
                time.sleep(1)
            else:
                raise RuntimeError('isolated PostgreSQL did not become ready')
            with gzip.open(received, 'rb') as source:
                restore = subprocess.Popen(['docker', 'exec', '-i', restore_name,
                                            'pg_restore', '--exit-on-error', '--no-owner',
                                            '--no-privileges', '-U', 'postgres', '-d', 'recovery'],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                # communicate avoids deadlock if PostgreSQL returns an error before EOF.
                _, error = restore.communicate(source.read(), timeout=300)
                if restore.returncode:
                    archive.with_name(archive.name + '.restore-error.log').write_bytes(error)
                    raise RuntimeError('pg_restore failed; output withheld')
            restored = fingerprint(restore_name, 'postgres', 'recovery')
            if restored != json.loads(received_manifest.read_text()):
                raise RuntimeError('restored content/catalog differs from snapshot invariants')
            evidence['restore_seconds'] = round(time.monotonic() - restore_start, 3)
            evidence['tables_verified'] = sum(row[0] == 'table' for row in restored)
            evidence['rows_verified'] = sum(row[2] for row in restored if row[0] == 'table')
            evidence['catalog_records_verified'] = sum(row[0] != 'table' for row in restored)
            evidence['invariants_sha256'] = sha256(received_manifest)
            evidence['restore_verified'] = True
    finally:
        if keeper is not None:
            keeper.communicate(b'ROLLBACK;\n\\q\n', timeout=15)
        if temporary_created:
            # Unique name is created by this invocation only; never remove source resources.
            run(['docker', 'rm', '-f', '-v', restore_name])
    evidence['temporary_resources_removed'] = True
    evidence['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    evidence['total_seconds'] = round(time.monotonic() - start, 3)
    evidence['retention'] = 'No automatic deletion; review capacity and retention before pruning'
    report = archive.with_name(archive.name + '.recovery.json')
    report.write_text(json.dumps(evidence, indent=2) + '\n')
    run(rsync + [str(report), host + ':' + remote + '/'])
    print(json.dumps(evidence, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    arguments = parser.parse_args()
    try:
        recover(json.loads(arguments.config.read_text()))
    except Exception as exc:
        # Do not print traceback, subprocess output, connection strings or SQL rows.
        print(f'Recovery failed: {type(exc).__name__}: {exc}', flush=True)
        raise SystemExit(1)

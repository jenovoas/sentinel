# 🎯 SemSH v0.3 - SSAP Integration Guide

## Nuevas Capacidades (DevOps Advisor)

SemSH ahora actúa como **Copiloto de Seguridad** siguiendo el Sentinel System Administration Protocol (SSAP).

### Comandos Especiales

#### 1. `health` - Health Advisor
Analiza el estado del sistema y sugiere acciones correctivas.

```bash
🧠 semsh> health

🏥 Sentinel Health Advisor (SSAP v1.0)
==================================================
CPU Load    : 85.2%
Memory Used : 14.1 GB
eBPF LSM    : ✅ ACTIVE
Relay       : ✅ RUNNING

⚠️  1 Issue(s) Detected:

🟡 [WARNING] High CPU Load (85.2%)
   → Suggested Action: Consider running: sctl tune --profile performance
```

#### 2. `review <comando>` - AI Command Review
La IA analiza un comando antes de ejecutarlo y advierte sobre riesgos.

```bash
🧠 semsh> review docker system prune -a

🔍 Reviewing: docker system prune -a
==================================================

🧠 AI Analysis:
Risk Level: HIGH

What it does:
- Removes all unused containers, networks, images (both dangling and unreferenced)
- Frees disk space but can delete cached build layers

Potential dangers:
- May delete images needed for quick rollback
- Build times will increase if images need to be re-pulled

Safer alternative:
docker image prune (removes only dangling images)
```

#### 3. `run <playbook>` - Execute Playbook
Ejecuta playbooks YAML predefinidos de forma segura.

```bash
🧠 semsh> run backup_db

📋 Executing Playbook: backup_critical_db
   Description: Realiza un backup completo de la base de datos PostgreSQL crítica.
   Risk Level: LOW

Proceed? [y/N]: y

▶️  Step: verify_disk_space
   Command: df -h /var/backups | awk 'NR==2 {if ($4 < 10) exit 1}'
✅ Success

▶️  Step: dump_database
   Command: sdocker exec postgres pg_dump -U sentinel db > /var/backups/sentinel_db_20260101.sql
✅ Success

✅ Playbook 'backup_db' completed successfully.
```

### Playbooks Disponibles

- `backup_db` - Backup de base de datos con verificación de integridad
- `cleanup_logs` - Limpieza segura de logs antiguos

### Integración con sctl

SemSH lee métricas del sistema vía `sctl status --json` para tomar decisiones informadas.

```python
# Internamente, SemSH ejecuta:
metrics = subprocess.run(['sctl', 'status', '--json'], ...)
# Y analiza: CPU, RAM, estado de eBPF, Relay, etc.
```

## Filosofía SSAP

**La IA propone, el Humano dispone.**

- SemSH **nunca** ejecuta comandos destructivos sin confirmación.
- Todos los playbooks requieren aprobación explícita (`y/N`).
- Los comandos pasan por validación semántica antes de llegar al kernel.

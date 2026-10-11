# Privileged Users Whitelist

**Last Updated:** vie 02 ene 2026 00:48:23 -03

## Overview
The following users are whitelisted and will NEVER be blocked by any Sentinel security mechanism:

- **root** (UID: 0)
- **jnovoas** (UID: 1000)

## Protected Systems
- fail2ban (IP-based, requires connection from localhost)
- PAM access control
- systemd service management
- eBPF kernel-level monitoring

## Configuration Files
- Whitelist: `config/privileged_users.sh`
- eBPF UIDs: `config/ebpf_whitelist.txt`
- Sudoers: `/etc/sudoers.d/sentinel-privileged`

## Important Notes
⚠ **Security Warning:** These users have unrestricted access. Use with caution.

To add/remove users, edit `config/privileged_users.sh` and re-run this script.

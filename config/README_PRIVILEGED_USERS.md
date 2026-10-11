# Privileged Users Protection System

## ✅ Status: CONFIGURED

**Whitelisted Users:** `root`, `jnovoas`

## What This Does

This system ensures that privileged users (root and jnovoas) are **NEVER blocked** by any Sentinel security mechanism, including:

- ✅ eBPF kernel-level monitoring
- ✅ systemd service management
- ✅ PAM access control
- ✅ fail2ban (IP-based)
- ✅ Custom security scripts

## Quick Start

### View Current Whitelist
```bash
cat /home/jnovoas/sentinel/config/privileged_users.sh
```

### Add a New User
1. Edit the configuration:
   ```bash
   nano /home/jnovoas/sentinel/config/privileged_users.sh
   ```

2. Add the username to the `PRIVILEGED_USERS` array:
   ```bash
   PRIVILEGED_USERS=(
       "root"
       "jnovoas"
       "newuser"  # Add here
   )
   ```

3. Re-run the configuration script:
   ```bash
   /home/jnovoas/sentinel/scripts/configure_privileged_users.sh
   ```

### Verify Configuration
```bash
# Check eBPF whitelist
cat /home/jnovoas/sentinel/config/ebpf_whitelist.txt

# Check sudoers rules
sudo cat /etc/sudoers.d/sentinel-privileged

# View documentation
cat /home/jnovoas/sentinel/docs/PRIVILEGED_USERS.md
```

## Integration with Security Systems

### eBPF Programs
Your eBPF programs should check against the whitelist before blocking:

```c
// In your eBPF program
u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;

// Check whitelist (UIDs: 0, 1000)
if (uid == 0 || uid == 1000) {
    return 0;  // Allow privileged users
}
```

### Python/Backend Services
```python
# Load whitelist
def is_privileged_user(uid: int) -> bool:
    with open('/home/jnovoas/sentinel/config/ebpf_whitelist.txt') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                whitelisted_uid = int(line.split()[0])
                if uid == whitelisted_uid:
                    return True
    return False

# Use in your code
if is_privileged_user(current_uid):
    logger.info(f"Skipping security check for privileged user {current_uid}")
    return  # Don't block
```

## Files Created

| File | Purpose |
|------|---------|
| `config/privileged_users.sh` | Main whitelist configuration |
| `config/ebpf_whitelist.txt` | UID list for eBPF programs |
| `/etc/sudoers.d/sentinel-privileged` | Sudoers rules for service management |
| `docs/PRIVILEGED_USERS.md` | Full documentation |

## Security Notes

⚠️ **WARNING:** Whitelisted users bypass ALL security checks. Use with extreme caution.

✅ **Best Practice:** Only whitelist users who need unrestricted access for system administration and development.

🔒 **Recommendation:** In production, remove development users from the whitelist.

## Troubleshooting

### User Still Getting Blocked?
1. Verify the user is in the whitelist:
   ```bash
   grep "jnovoas" /home/jnovoas/sentinel/config/privileged_users.sh
   ```

2. Check UID matches:
   ```bash
   id -u jnovoas
   cat /home/jnovoas/sentinel/config/ebpf_whitelist.txt
   ```

3. Re-run configuration:
   ```bash
   /home/jnovoas/sentinel/scripts/configure_privileged_users.sh
   ```

4. Restart security services:
   ```bash
   sudo systemctl restart fail2ban
   sudo systemctl restart sentinel-*
   ```

## Support

For issues or questions, check the main documentation or contact the system administrator.

---

**Last Updated:** $(date)
**Version:** 1.0.0

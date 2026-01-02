#!/bin/bash
# Sentinel Privileged User Protection
# Ensures privileged users are never blocked by security systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHITELIST_CONFIG="$SCRIPT_DIR/../config/privileged_users.sh"

# Load privileged users
if [ -f "$WHITELIST_CONFIG" ]; then
    source "$WHITELIST_CONFIG"
else
    echo "[ERROR] Whitelist configuration not found: $WHITELIST_CONFIG"
    exit 1
fi

echo "[INFO] Configuring privileged user protection..."
echo "[INFO] Privileged users: ${PRIVILEGED_USERS[*]}"

# 1. Configure fail2ban to ignore privileged users
configure_fail2ban() {
    local FAIL2BAN_CONF="/etc/fail2ban/jail.local"
    
    if [ ! -f "$FAIL2BAN_CONF" ]; then
        echo "[WARN] fail2ban not configured, skipping..."
        return
    fi

    echo "[INFO] Configuring fail2ban whitelist..."
    
    # Create ignoreip list
    local IGNORE_IPS="127.0.0.1 ::1"
    
    # Backup original config
    sudo cp "$FAIL2BAN_CONF" "${FAIL2BAN_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add privileged users to ignorecommand (if supported)
    # Note: fail2ban works with IPs, not users, so we document this limitation
    echo "[WARN] fail2ban works with IPs. Privileged users must connect from whitelisted IPs."
    echo "[INFO] Current whitelisted IPs: $IGNORE_IPS"
}

# 2. Configure PAM to allow privileged users
configure_pam() {
    echo "[INFO] Configuring PAM exceptions for privileged users..."
    
    local PAM_ACCESS="/etc/security/access.conf"
    
    if [ ! -f "$PAM_ACCESS" ]; then
        echo "[WARN] PAM access.conf not found, skipping..."
        return
    fi
    
    # Backup
    sudo cp "$PAM_ACCESS" "${PAM_ACCESS}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add privileged users to allow list
    for user in "${PRIVILEGED_USERS[@]}"; do
        if ! sudo grep -q "^+ : $user : ALL" "$PAM_ACCESS" 2>/dev/null; then
            echo "+ : $user : ALL" | sudo tee -a "$PAM_ACCESS" > /dev/null
            echo "[INFO] Added $user to PAM whitelist"
        fi
    done
}

# 3. Create systemd override to prevent service blocks
configure_systemd() {
    echo "[INFO] Configuring systemd service protection..."
    
    # Ensure privileged users can always restart services
    local SUDOERS_FILE="/etc/sudoers.d/sentinel-privileged"
    
    {
        echo "# Sentinel Privileged Users - Auto-generated"
        echo "# These users can manage Sentinel services without restrictions"
        for user in "${PRIVILEGED_USERS[@]}"; do
            echo "$user ALL=(ALL) NOPASSWD: /bin/systemctl restart sentinel-*"
            echo "$user ALL=(ALL) NOPASSWD: /bin/systemctl stop sentinel-*"
            echo "$user ALL=(ALL) NOPASSWD: /bin/systemctl start sentinel-*"
            echo "$user ALL=(ALL) NOPASSWD: /bin/systemctl status sentinel-*"
        done
    } | sudo tee "$SUDOERS_FILE" > /dev/null
    
    sudo chmod 0440 "$SUDOERS_FILE"
    echo "[INFO] Created sudoers rules for privileged users"
}

# 4. Create eBPF whitelist (if applicable)
configure_ebpf_whitelist() {
    local EBPF_WHITELIST="/home/jnovoas/sentinel/config/ebpf_whitelist.txt"
    
    echo "[INFO] Creating eBPF whitelist..."
    
    {
        echo "# Sentinel eBPF Whitelist - Auto-generated"
        echo "# UIDs of users that should never be blocked"
        for user in "${PRIVILEGED_USERS[@]}"; do
            uid=$(id -u "$user" 2>/dev/null || echo "")
            if [ -n "$uid" ]; then
                echo "$uid  # $user"
            fi
        done
    } > "$EBPF_WHITELIST"
    
    echo "[INFO] eBPF whitelist created at $EBPF_WHITELIST"
}

# 5. Document the whitelist
create_documentation() {
    local DOC_FILE="/home/jnovoas/sentinel/docs/PRIVILEGED_USERS.md"
    
    mkdir -p "$(dirname "$DOC_FILE")"
    
    {
        echo "# Privileged Users Whitelist"
        echo ""
        echo "**Last Updated:** $(date)"
        echo ""
        echo "## Overview"
        echo "The following users are whitelisted and will NEVER be blocked by any Sentinel security mechanism:"
        echo ""
        for user in "${PRIVILEGED_USERS[@]}"; do
            uid=$(id -u "$user" 2>/dev/null || echo "N/A")
            echo "- **$user** (UID: $uid)"
        done
        echo ""
        echo "## Protected Systems"
        echo "- fail2ban (IP-based, requires connection from localhost)"
        echo "- PAM access control"
        echo "- systemd service management"
        echo "- eBPF kernel-level monitoring"
        echo ""
        echo "## Configuration Files"
        echo "- Whitelist: \`config/privileged_users.sh\`"
        echo "- eBPF UIDs: \`config/ebpf_whitelist.txt\`"
        echo "- Sudoers: \`/etc/sudoers.d/sentinel-privileged\`"
        echo ""
        echo "## Important Notes"
        echo "⚠️ **Security Warning:** These users have unrestricted access. Use with caution."
        echo ""
        echo "To add/remove users, edit \`config/privileged_users.sh\` and re-run this script."
    } > "$DOC_FILE"
    
    echo "[INFO] Documentation created at $DOC_FILE"
}

# Main execution
main() {
    echo "========================================="
    echo "  Sentinel Privileged User Protection"
    echo "========================================="
    echo ""
    
    configure_fail2ban
    configure_pam
    configure_systemd
    configure_ebpf_whitelist
    create_documentation
    
    echo ""
    echo "========================================="
    echo "✅ Privileged user protection configured!"
    echo "========================================="
    echo ""
    echo "Whitelisted users: ${PRIVILEGED_USERS[*]}"
    echo ""
    echo "⚠️  IMPORTANT: Restart security services for changes to take effect:"
    echo "   sudo systemctl restart fail2ban"
    echo ""
}

main "$@"

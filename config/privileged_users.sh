#!/bin/bash
# Sentinel Privileged Users Whitelist
# Users in this list will NEVER be blocked by any security mechanism

PRIVILEGED_USERS=(
    "root"
    "jnovoas"
)

# Function to check if a user is privileged
is_privileged_user() {
    local username="$1"
    for user in "${PRIVILEGED_USERS[@]}"; do
        if [ "$user" = "$username" ]; then
            return 0  # User is privileged
        fi
    done
    return 1  # User is not privileged
}

# Export for use in other scripts
export -f is_privileged_user
export PRIVILEGED_USERS

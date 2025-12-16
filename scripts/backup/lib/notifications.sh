#!/bin/bash
#
# Sentinel Backup System - Notifications Module
#
# This module handles sending notifications via webhooks (Slack, Discord, etc.)
# for backup events such as success, failure, and warnings.
#
# Usage:
#   source "$(dirname "$0")/lib/notifications.sh"
#   send_notification "success" "Backup completed successfully"
#   send_notification "error" "Backup failed"
#
# Notification Types:
#   success - Successful operations (green)
#   error   - Failed operations (red)
#   warning - Warning messages (yellow)
#   info    - Informational messages (blue)
#

set -euo pipefail

# ============================================================================
# CONSTANTS
# ============================================================================

# Emoji for different notification types
readonly EMOJI_SUCCESS="✅"
readonly EMOJI_ERROR="🚨"
readonly EMOJI_WARNING="⚠️"
readonly EMOJI_INFO="ℹ️"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

#
# Get emoji for notification type
#
# Args:
#   $1 - Notification type (success, error, warning, info)
#
# Returns:
#   Emoji string
#
get_emoji() {
    local type="${1:-info}"
    
    case "${type,,}" in
        success) echo "$EMOJI_SUCCESS" ;;
        error)   echo "$EMOJI_ERROR" ;;
        warning) echo "$EMOJI_WARNING" ;;
        info)    echo "$EMOJI_INFO" ;;
        *)       echo "$EMOJI_INFO" ;;
    esac
}

#
# Check if notifications are enabled
#
# Returns:
#   0 if enabled, 1 if disabled
#
is_notification_enabled() {
    # Check if webhook is enabled
    if [[ "${WEBHOOK_ENABLED:-false}" != "true" ]]; then
        return 1
    fi
    
    # Check if webhook URL is set
    if [[ -z "${WEBHOOK_URL:-}" ]]; then
        return 1
    fi
    
    return 0
}

#
# Check if notification should be sent based on level
#
# Args:
#   $1 - Notification type (success, error, warning, info)
#
# Returns:
#   0 if should send, 1 if should skip
#
should_send_notification() {
    local type="${1:-info}"
    local level="${NOTIFICATION_LEVEL:-error}"
    
    case "${level,,}" in
        all)
            # Send all notifications
            return 0
            ;;
        error)
            # Only send error notifications
            if [[ "${type,,}" == "error" ]]; then
                return 0
            fi
            return 1
            ;;
        none)
            # Don't send any notifications
            return 1
            ;;
        *)
            # Default: only errors
            if [[ "${type,,}" == "error" ]]; then
                return 0
            fi
            return 1
            ;;
    esac
}

# ============================================================================
# NOTIFICATION FUNCTIONS
# ============================================================================

#
# Send notification to webhook
#
# Args:
#   $1 - Notification type (success, error, warning, info)
#   $2 - Message text
#   $3 - Additional details (optional)
#
send_notification() {
    local type="${1:-info}"
    local message="${2:-}"
    local details="${3:-}"
    
    # Check if notifications are enabled
    if ! is_notification_enabled; then
        return 0
    fi
    
    # Check if notification should be sent based on level
    if ! should_send_notification "$type"; then
        return 0
    fi
    
    # Get emoji for notification type
    local emoji=$(get_emoji "$type")
    
    # Build message
    local full_message="$emoji **Sentinel Backup** - $message"
    if [[ -n "$details" ]]; then
        full_message="$full_message\n\`\`\`\n$details\n\`\`\`"
    fi
    
    # Send to webhook
    send_webhook "$full_message"
}

#
# Send raw message to webhook
#
# Args:
#   $1 - Message text
#
send_webhook() {
    local message="$1"
    local webhook_url="${WEBHOOK_URL:-}"
    
    if [[ -z "$webhook_url" ]]; then
        return 0
    fi
    
    # Detect webhook type and format accordingly
    if [[ "$webhook_url" =~ slack\.com ]]; then
        send_slack_webhook "$message"
    elif [[ "$webhook_url" =~ discord\.com ]]; then
        send_discord_webhook "$message"
    else
        # Generic webhook (assume Slack format)
        send_slack_webhook "$message"
    fi
}

#
# Send notification to Slack webhook
#
# Args:
#   $1 - Message text
#
send_slack_webhook() {
    local message="$1"
    local webhook_url="${WEBHOOK_URL:-}"
    
    # Format message for Slack
    local payload=$(cat <<EOF
{
  "text": "$message",
  "username": "Sentinel Backup",
  "icon_emoji": ":shield:"
}
EOF
)
    
    # Send to Slack
    curl -s -X POST "$webhook_url" \
        -H 'Content-Type: application/json' \
        -d "$payload" \
        > /dev/null 2>&1 || true
}

#
# Send notification to Discord webhook
#
# Args:
#   $1 - Message text
#
send_discord_webhook() {
    local message="$1"
    local webhook_url="${WEBHOOK_URL:-}"
    
    # Format message for Discord
    local payload=$(cat <<EOF
{
  "content": "$message",
  "username": "Sentinel Backup"
}
EOF
)
    
    # Send to Discord
    curl -s -X POST "$webhook_url" \
        -H 'Content-Type: application/json' \
        -d "$payload" \
        > /dev/null 2>&1 || true
}

#
# Send success notification
#
# Args:
#   $1 - Message text
#   $2 - Additional details (optional)
#
notify_success() {
    send_notification "success" "$1" "${2:-}"
}

#
# Send error notification
#
# Args:
#   $1 - Message text
#   $2 - Additional details (optional)
#
notify_error() {
    send_notification "error" "$1" "${2:-}"
}

#
# Send warning notification
#
# Args:
#   $1 - Message text
#   $2 - Additional details (optional)
#
notify_warning() {
    send_notification "warning" "$1" "${2:-}"
}

#
# Send info notification
#
# Args:
#   $1 - Message text
#   $2 - Additional details (optional)
#
notify_info() {
    send_notification "info" "$1" "${2:-}"
}

# ============================================================================
# EXPORTS
# ============================================================================

# Export notification functions
export -f get_emoji
export -f is_notification_enabled
export -f should_send_notification
export -f send_notification
export -f send_webhook
export -f send_slack_webhook
export -f send_discord_webhook
export -f notify_success
export -f notify_error
export -f notify_warning
export -f notify_info

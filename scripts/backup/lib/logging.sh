#!/bin/bash
#
# Sentinel Backup System - Logging Module
#
# This module provides structured logging functionality with multiple log levels,
# file and stdout output, and formatted timestamps.
#
# Usage:
#   source "$(dirname "$0")/lib/logging.sh"
#   log_info "Backup started"
#   log_error "Backup failed"
#
# Log Levels:
#   DEBUG - Detailed information for diagnosing problems
#   INFO  - General informational messages
#   WARN  - Warning messages for potentially harmful situations
#   ERROR - Error messages for serious problems
#

set -euo pipefail

# ============================================================================
# CONSTANTS
# ============================================================================

readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARN=2
readonly LOG_LEVEL_ERROR=3

# ANSI color codes
readonly COLOR_RESET='\033[0m'
readonly COLOR_DEBUG='\033[0;36m'   # Cyan
readonly COLOR_INFO='\033[0;32m'    # Green
readonly COLOR_WARN='\033[1;33m'    # Yellow
readonly COLOR_ERROR='\033[0;31m'   # Red

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

#
# Get numeric log level from string
#
# Args:
#   $1 - Log level string (DEBUG, INFO, WARN, ERROR)
#
# Returns:
#   Numeric log level (0-3)
#
get_log_level_number() {
    local level="${1:-INFO}"
    
    case "${level^^}" in
        DEBUG) echo $LOG_LEVEL_DEBUG ;;
        INFO)  echo $LOG_LEVEL_INFO ;;
        WARN)  echo $LOG_LEVEL_WARN ;;
        ERROR) echo $LOG_LEVEL_ERROR ;;
        *)     echo $LOG_LEVEL_INFO ;;
    esac
}

#
# Get current configured log level number
#
get_current_log_level() {
    get_log_level_number "${LOG_LEVEL:-INFO}"
}

#
# Format timestamp for log messages
#
# Returns:
#   Formatted timestamp string (YYYY-MM-DD HH:MM:SS)
#
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

#
# Write log message to file
#
# Args:
#   $1 - Log message
#
write_to_log_file() {
    local message="$1"
    local log_file="${LOG_FILE:-/var/log/sentinel-backup.log}"
    
    # Create log directory if it doesn't exist
    local log_dir=$(dirname "$log_file")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" 2>/dev/null || true
    fi
    
    # Write to log file if writable
    if [[ -w "$log_dir" ]] || [[ -w "$log_file" ]]; then
        echo "$message" >> "$log_file" 2>/dev/null || true
    fi
}

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

#
# Generic log function
#
# Args:
#   $1 - Log level (DEBUG, INFO, WARN, ERROR)
#   $2 - Log message
#   $3 - Color code (optional)
#
log_message() {
    local level="$1"
    local message="$2"
    local color="${3:-$COLOR_RESET}"
    
    # Get numeric log levels
    local level_num=$(get_log_level_number "$level")
    local current_level=$(get_current_log_level)
    
    # Skip if message level is below current log level
    if [[ $level_num -lt $current_level ]]; then
        return 0
    fi
    
    # Format message
    local timestamp=$(get_timestamp)
    local formatted_message="[$timestamp] [$level] $message"
    
    # Write to stdout if enabled
    if [[ "${LOG_TO_STDOUT:-true}" == "true" ]]; then
        if [[ -t 1 ]]; then
            # Terminal supports colors
            echo -e "${color}${formatted_message}${COLOR_RESET}"
        else
            # No color support
            echo "$formatted_message"
        fi
    fi
    
    # Write to log file if enabled
    if [[ "${LOG_TO_FILE:-true}" == "true" ]]; then
        write_to_log_file "$formatted_message"
    fi
}

#
# Log debug message
#
# Args:
#   $1 - Log message
#
log_debug() {
    log_message "DEBUG" "$1" "$COLOR_DEBUG"
}

#
# Log info message
#
# Args:
#   $1 - Log message
#
log_info() {
    log_message "INFO" "$1" "$COLOR_INFO"
}

#
# Log warning message
#
# Args:
#   $1 - Log message
#
log_warn() {
    log_message "WARN" "$1" "$COLOR_WARN"
}

#
# Log error message
#
# Args:
#   $1 - Log message
#
log_error() {
    log_message "ERROR" "$1" "$COLOR_ERROR"
}

#
# Log success message (alias for info with checkmark)
#
# Args:
#   $1 - Log message
#
log_success() {
    log_info "✓ $1"
}

#
# Log failure message (alias for error with X mark)
#
# Args:
#   $1 - Log message
#
log_failure() {
    log_error "✗ $1"
}

#
# Log section header
#
# Args:
#   $1 - Section title
#
log_section() {
    local title="$1"
    local separator="========================================"
    
    log_info "$separator"
    log_info "$title"
    log_info "$separator"
}

# ============================================================================
# EXPORTS
# ============================================================================

# Export logging functions
export -f get_log_level_number
export -f get_current_log_level
export -f get_timestamp
export -f write_to_log_file
export -f log_message
export -f log_debug
export -f log_info
export -f log_warn
export -f log_error
export -f log_success
export -f log_failure
export -f log_section

#!/bin/bash

# load_sentinel_context.sh
# Centralized logic to gather system and local context for ME-60OS

get_sentinel_context() {
    local context=""
    local project_root=""
    
    # 1. Find project root (looking for .git or .gemini/system.md)
    local current_dir="$PWD"
    while [[ "$current_dir" != "/" ]]; do
        if [[ -d "$current_dir/.git" ]] || [[ -f "$current_dir/.gemini/system.md" ]]; then
            project_root="$current_dir"
            break
        fi
        current_dir=$(dirname "$current_dir")
    done

    # 2. Add System Prompt
    if [[ -n "$project_root" ]] && [[ -f "$project_root/.gemini/system.md" ]]; then
        context=$(cat "$project_root/.gemini/system.md")
    fi

    # 3. Add Local Agent Context (Search upwards from PWD to project_root)
    local search_dir="$PWD"
    while [[ "$search_dir" != "$project_root" ]] && [[ "$search_dir" != "/" ]]; do
        if [[ -f "$search_dir/agents.md" ]]; then
            context="$context\n\n--- LOCAL AGENT CONTEXT ($search_dir/agents.md) ---\n$(cat "$search_dir/agents.md")"
            break # Stop at the first (closest) agent context
        fi
        search_dir=$(dirname "$search_dir")
    done
    
    # Also check project root for agents.md if not already found
    if [[ "$search_dir" == "$project_root" ]] && [[ -f "$project_root/agents.md" ]]; then
        context="$context\n\n--- PROJECT AGENT CONTEXT ($project_root/agents.md) ---\n$(cat "$project_root/agents.md")"
    fi

    echo -e "$context"
}

# If executed directly, output the context
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_sentinel_context
fi

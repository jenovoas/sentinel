#!/bin/bash

# load_sentinel_context.sh
# Centralized logic to gather system and local context for ME-60OS and Sentinel

get_sentinel_context() {
    local context=""
    local project_root=""
    local project_type="Generic"
    
    # 1. Find project root (looking for .git or .gemini/system.md)
    local current_dir="$PWD"
    while [[ "$current_dir" != "/" ]]; do
        if [[ -d "$current_dir/.git" ]] || [[ -f "$current_dir/.gemini/system.md" ]]; then
            project_root="$current_dir"
            break
        fi
        current_dir=$(dirname "$current_dir")
    done

    # 2. Identify Project Type and Add System Prompt
    if [[ -n "$project_root" ]]; then
        if [[ "$project_root" == *"/sentinel" ]]; then
            project_type="Sentinel (Infrastructure)"
        elif [[ "$project_root" == *"/ME-60OS" ]]; then
            project_type="ME-60OS (Devices/Robotics)"
        fi

        if [[ -f "$project_root/.gemini/system.md" ]]; then
            context="--- PROJECT SYSTEM PROMPT ($project_type) ---\n$(cat "$project_root/.gemini/system.md")"
        elif [[ -f "$project_root/AI_SYSTEM_PROMPT.md" ]]; then
            # Legacy/Fallback
            context="--- PROJECT SYSTEM PROMPT ($project_type - Fallback) ---\n$(cat "$project_root/AI_SYSTEM_PROMPT.md")"
        fi
        
        # Add Project-Wide Agents/Skills
        if [[ -f "$project_root/agents.md" ]]; then
            context="$context\n\n--- PROJECT-WIDE AGENTS ($project_root/agents.md) ---\n$(cat "$project_root/agents.md")"
        fi
        if [[ -f "$project_root/skills.md" ]]; then
            context="$context\n\n--- PROJECT-WIDE SKILLS ($project_root/skills.md) ---\n$(cat "$project_root/skills.md")"
        fi
    fi

    # 3. Add Local Context (Search upwards from PWD to project_root, non-inclusive of root already added)
    local search_dir="$PWD"
    while [[ "$search_dir" != "$project_root" ]] && [[ "$search_dir" != "/" ]]; do
        if [[ -f "$search_dir/agents.md" ]]; then
            context="$context\n\n--- LOCAL AGENT CONTEXT ($search_dir/agents.md) ---\n$(cat "$search_dir/agents.md")"
            # Note: We continue upwards to capture nested agents if needed, 
            # or stop here if we only want the closest. The current architecture 
            # suggests we might want all levels of context. 
            # To keep it lean, we take the closest one in subdirs.
            break 
        fi
        search_dir=$(dirname "$search_dir")
    done
    
    # 4. Local _AI_CONTEXT.md (Directory-specific rules)
    if [[ -f "$PWD/_AI_CONTEXT.md" ]]; then
        context="$context\n\n--- DIRECTORY RULES ($PWD/_AI_CONTEXT.md) ---\n$(cat "$PWD/_AI_CONTEXT.md")"
    fi

    echo -e "$context"
}

# If executed directly, output the context
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_sentinel_context
fi

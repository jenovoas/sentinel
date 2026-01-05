#!/bin/bash
# Sentinel TUI Installation Script
# Installs dependencies and configures Neovim integration

set -e

echo "🛡️ Installing Sentinel TUI..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running in Sentinel directory
if [ ! -f "sentinel_tui.py" ]; then
    echo "❌ Error: Must run from Sentinel root directory"
    exit 1
fi

# Activate virtual environment
if [ -d ".venv" ]; then
    echo -e "${BLUE}🐍 Using Sentinel virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found. Creating one...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install textual rich httpx

# Make TUI executable
chmod +x sentinel_tui.py

# Create symlink in user bin
echo -e "${BLUE}🔗 Creating symlink...${NC}"
mkdir -p ~/.local/bin
ln -sf "$(pwd)/sentinel_tui.py" ~/.local/bin/sentinel-tui

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}⚠️  Adding ~/.local/bin to PATH${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

# Create Neovim integration
echo -e "${BLUE}📝 Configuring Neovim integration...${NC}"

NVIM_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"
SENTINEL_PLUGIN_DIR="$NVIM_CONFIG_DIR/lua/sentinel"

mkdir -p "$SENTINEL_PLUGIN_DIR"

# Create Neovim Lua plugin
cat > "$SENTINEL_PLUGIN_DIR/init.lua" << 'EOF'
-- Sentinel TUI Integration for Neovim
-- Provides AI-powered system administration from within Neovim

local M = {}

-- Configuration
M.config = {
    terminal_cmd = "sentinel-tui",
    window_height = 20,
    window_width = 100,
}

-- Open Sentinel TUI in a terminal split
function M.open()
    vim.cmd('botright ' .. M.config.window_height .. 'split')
    vim.cmd('terminal ' .. M.config.terminal_cmd)
    vim.cmd('startinsert')
end

-- Open Sentinel TUI in a floating window
function M.open_float()
    local buf = vim.api.nvim_create_buf(false, true)
    
    -- Calculate window size
    local width = M.config.window_width
    local height = M.config.window_height
    local row = math.floor((vim.o.lines - height) / 2)
    local col = math.floor((vim.o.columns - width) / 2)
    
    -- Create floating window
    local opts = {
        relative = 'editor',
        width = width,
        height = height,
        row = row,
        col = col,
        style = 'minimal',
        border = 'rounded',
        title = ' Sentinel TUI ',
        title_pos = 'center',
    }
    
    local win = vim.api.nvim_open_win(buf, true, opts)
    
    -- Open terminal in buffer
    vim.fn.termopen(M.config.terminal_cmd)
    vim.cmd('startinsert')
end

-- Ask Sentinel AI about current buffer
function M.ask_about_buffer()
    local bufnr = vim.api.nvim_get_current_buf()
    local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
    local content = table.concat(lines, '\n')
    local filetype = vim.bo.filetype
    
    -- Create temp file with buffer content
    local tmpfile = os.tmpname()
    local f = io.open(tmpfile, 'w')
    f:write(content)
    f:close()
    
    -- Ask AI about the code
    local question = vim.fn.input('Ask Sentinel AI: ')
    if question ~= '' then
        local cmd = string.format(
            "sentinel-tui --query 'Analyze this %s code and %s: %s'",
            filetype, question, tmpfile
        )
        vim.cmd('botright 15split | terminal ' .. cmd)
    end
    
    os.remove(tmpfile)
end

-- Deploy specific agent
function M.deploy_agent(agent_name)
    local cmd = string.format("sentinel-tui --agent %s", agent_name)
    vim.cmd('botright 20split | terminal ' .. cmd)
    vim.cmd('startinsert')
end

-- Setup keymaps
function M.setup(opts)
    M.config = vim.tbl_extend('force', M.config, opts or {})
    
    -- Default keymaps
    vim.keymap.set('n', '<leader>st', M.open, { desc = 'Open Sentinel TUI' })
    vim.keymap.set('n', '<leader>sf', M.open_float, { desc = 'Open Sentinel TUI (float)' })
    vim.keymap.set('n', '<leader>sa', M.ask_about_buffer, { desc = 'Ask Sentinel about buffer' })
    vim.keymap.set('n', '<leader>s1', function() M.deploy_agent('security') end, { desc = 'Deploy Security Agent' })
    vim.keymap.set('n', '<leader>s2', function() M.deploy_agent('devops') end, { desc = 'Deploy DevOps Agent' })
    vim.keymap.set('n', '<leader>s3', function() M.deploy_agent('quantum') end, { desc = 'Deploy Quantum Agent' })
    
    print('🛡️ Sentinel TUI loaded')
end

return M
EOF

# Create example Neovim config snippet
cat > "$SENTINEL_PLUGIN_DIR/example_config.lua" << 'EOF'
-- Add this to your init.lua or init.vim (as Lua)

-- Load Sentinel plugin
require('sentinel').setup({
    window_height = 20,
    window_width = 100,
})

-- Keybindings (already set by setup, but you can customize):
-- <leader>st  - Open Sentinel TUI in split
-- <leader>sf  - Open Sentinel TUI in floating window
-- <leader>sa  - Ask Sentinel about current buffer
-- <leader>s1  - Deploy Security Agent
-- <leader>s2  - Deploy DevOps Agent
-- <leader>s3  - Deploy Quantum Agent
EOF

echo -e "${GREEN}✅ Sentinel TUI installed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1. Add to your Neovim config (~/.config/nvim/init.lua):"
echo "   require('sentinel').setup()"
echo ""
echo "2. Restart Neovim or run: :luafile ~/.config/nvim/lua/sentinel/init.lua"
echo ""
echo "3. Use these keybindings in Neovim:"
echo "   <leader>st  - Open Sentinel TUI"
echo "   <leader>sf  - Open Sentinel TUI (floating)"
echo "   <leader>sa  - Ask about current buffer"
echo ""
echo "4. Or run directly from terminal:"
echo "   sentinel-tui"
echo ""
echo -e "${YELLOW}⚠️  Make sure Sentinel backend is running:${NC}"
echo "   cd /home/jnovoas/sentinel && docker-compose up -d backend"
echo ""
echo -e "${GREEN}🎉 Happy coding with Sentinel AI!${NC}"

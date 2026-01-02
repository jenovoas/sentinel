# Sentinel Development Configuration

## Editor Settings

This directory contains development environment configurations for Sentinel.

### Included Configurations

1. **VSCode Settings** - `.vscode/settings.json`
2. **EditorConfig** - `.editorconfig`
3. **Prettier** - `.prettierrc`
4. **ESLint** - `.eslintrc.json`
5. **TypeScript** - `tsconfig.json`
6. **Git** - `.gitignore`, `.gitattributes`

### Neovim/Vim Configuration

For Neovim users, we provide a complete LSP setup with:
- TypeScript/JavaScript support
- Python support
- Auto-completion
- Linting and formatting
- File navigation
- Git integration

See `nvim/` directory for configuration files.

### Quick Setup

```bash
# Install dependencies
npm install

# Setup pre-commit hooks
npm run prepare

# Start development
npm run dev
```

### Code Style

- **Indentation**: 2 spaces
- **Line Length**: 100 characters
- **Quotes**: Double quotes for strings
- **Semicolons**: Required
- **Trailing Commas**: ES5 style

### Recommended Extensions

#### VSCode
- ESLint
- Prettier
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- GitLens

#### Neovim
- nvim-lspconfig
- nvim-cmp
- null-ls.nvim
- telescope.nvim
- nvim-treesitter

### Keyboard Shortcuts

See `KEYBINDINGS.md` for complete list of shortcuts.

---

**Sentinel Development Team**

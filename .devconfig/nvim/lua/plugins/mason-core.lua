-- lua/plugins/mason-core.lua
return {
  "williamboman/mason.nvim",
  opts = {
    ensure_installed = {
      -- LSP servers not handled by mason-lspconfig.nvim's ensure_installed
      "typescript-language-server", -- Installed directly by Mason

      -- formatters
      "prettierd",
      "stylua",
      "isort",
      "black",
      "gofmt",

      -- linters
      "codespell",
    },
  },
}

return {
  -- 2. MASON-LSPCONFIG (El puente)
  {
    "williamboman/mason-lspconfig.nvim",
    -- IMPORTANTE: Aquí está la corrección. Fijamos la versión v1.31.0
    -- que es la última compatible con setup_handlers.
    tag = "v1.31.0", 
    opts = {
       ensure_installed = {
         "lua_ls",
         "jsonls",
         "html",
         "cssls",
         "pyright",
         "gopls",
         "rust_analyzer",
         "yamlls",
         "dockerls",
         "marksman",
         "bashls",
       },
       automatic_installation = true, 
    },
  },

  -- 3. NVIM-LSPCONFIG (El motor)
  {
    "neovim/nvim-lspconfig",
    tag = "v1.0.0", -- Mantenemos esta versión estable
    config = function()
      local lspconfig = require("lspconfig")
      local mason_lspconfig = require("mason-lspconfig")

      local capabilities = vim.lsp.protocol.make_client_capabilities()
      capabilities.textDocument.completion.completionItem.snippetSupport = true

      local on_attach = function(client, bufnr)
        client.server_capabilities.documentFormattingProvider = false
        client.server_capabilities.documentRangeFormattingProvider = false

        local function buf_set_keymap(...) vim.api.nvim_buf_set_keymap(bufnr, ...) end
        local function buf_set_option(...) vim.api.nvim_buf_set_option(bufnr, ...) end

        buf_set_option('omnifunc', 'v:lua.vim.lsp.omnifunc')

        buf_set_keymap('n', 'gD', '<cmd>lua vim.lsp.buf.declaration()<CR>', { desc = 'Go to Declaration' })
        buf_set_keymap('n', 'gd', '<cmd>lua vim.lsp.buf.definition()<CR>', { desc = 'Go to Definition' })
        buf_set_keymap('n', 'K', '<cmd>lua vim.lsp.buf.hover()<CR>', { desc = 'Hover Documentation' })
        buf_set_keymap('n', 'gi', '<cmd>lua vim.lsp.buf.implementation()<CR>', { desc = 'Go to Implementation' })
        buf_set_keymap('n', '<C-k>', '<cmd>lua vim.lsp.buf.signature_help()<CR>', { desc = 'Signature Help' })
        buf_set_keymap('n', '<leader>wa', '<cmd>lua vim.lsp.buf.add_workspace_folder()<CR>', { desc = 'Add Workspace Folder' })
        buf_set_keymap('n', '<leader>wr', '<cmd>lua vim.lsp.buf.remove_workspace_folder()<CR>', { desc = 'Remove Workspace Folder' })
        buf_set_keymap('n', '<leader>wl', '<cmd>lua print(vim.inspect(vim.lsp.buf.list_workspace_folders()))<CR>', { desc = 'List Workspace Folders' })
        buf_set_keymap('n', '<leader>D', '<cmd>lua vim.lsp.buf.type_definition()<CR>', { desc = 'Go to Type Definition' })
        buf_set_keymap('n', '<leader>rn', '<cmd>lua vim.lsp.buf.rename()<CR>', { desc = 'Rename' })
        buf_set_keymap('n', '<leader>ca', '<cmd>lua vim.lsp.buf.code_action()<CR>', { desc = 'Code Action' })
        buf_set_keymap('n', 'gr', '<cmd>lua vim.lsp.buf.references()<CR>', { desc = 'Go to References' })
        buf_set_keymap('n', '[d', '<cmd>lua vim.diagnostic.goto_prev()<CR>', { desc = 'Previous Diagnostic' })
        buf_set_keymap('n', ']d', '<cmd>lua vim.diagnostic.goto_next()<CR>', { desc = 'Next Diagnostic' })
        buf_set_keymap('n', '<leader>e', '<cmd>lua vim.diagnostic.open_float()<CR>', { desc = 'Open Diagnostic Float' })
        buf_set_keymap('n', '<leader>q', '<cmd>lua vim.diagnostic.set_loclist()<CR>', { desc = 'Set Diagnostic Loclist' })
        buf_set_keymap('n', '<leader>f', '<cmd>lua vim.lsp.buf.format()<CR>', { desc = 'Format Document (LSP)' })

        if client.server_capabilities.documentHighlightProvider then
          vim.api.nvim_exec(
            [[
            augroup lsp_document_highlight
              autocmd! * <buffer>
              autocmd CursorHold <buffer> lua vim.lsp.buf.document_highlight()
              autocmd CursorMoved <buffer> lua vim.lsp.buf.clear_references()
            augroup END
            ]],
            false
          )
        end
      end

      -- Esta función ahora SÍ funcionará porque estamos usando la versión 1.31.0
      mason_lspconfig.setup_handlers({
        function(server_name)
          lspconfig[server_name].setup({
            on_attach = on_attach,
            capabilities = capabilities,
          })
        end,
      })

      vim.diagnostic.config({
        virtual_text = true,
        signs = true,
        update_in_insert = false,
        float = {
          source = "always",
          border = "single",
        },
      })

      vim.api.nvim_create_autocmd("LspAttach", {
        group = vim.api.nvim_create_augroup("lsp_attach", { clear = true }),
        callback = function(args)
          local client = vim.lsp.get_client_by_id(args.data.client_id)
          if client.supports_method("textDocument/hover") then
            vim.api.nvim_buf_set_keymap(args.buf, "n", "<M-]>", "<cmd>lua vim.lsp.buf.hover()<CR>", { desc = "Hover Documentation" })
          end
        end,
      })
    end,
  },
}

-- lua/plugins/formatting.lua
return {
  "stevearc/conform.nvim",
  event = { "BufReadPre", "BufNewFile" }, -- Cargar al abrir un archivo
  config = function()
    local conform = require("conform")

    conform.setup({
      formatters_by_ft = {
        -- Lua: Usar stylua (el estándar)
        lua = { "stylua" },
        
        -- Web (JS, TS, HTML, CSS, JSON): Usar Prettier
        -- Usamos prettierd, una versión más rápida que corre como un demonio
        javascript = { "prettierd" },
        typescript = { "prettierd" },
        javascriptreact = { "prettierd" },
        typescriptreact = { "prettierd" },
        css = { "prettierd" },
        html = { "prettierd" },
        json = { "prettierd" },
        yaml = { "prettierd" },
        markdown = { "prettierd" },
        graphql = { "prettierd" },

        -- Python: Usar isort (ordenar imports) y black (formateo)
        python = { "isort", "black" },
        
        -- Go
        go = { "gofmt" },

        -- Fallback: Si no hay nada específico, intentar usar el LSP
        -- (útil para lenguajes donde el LSP formatea bien, como Rust o Go)
        ["*"] = { "codespell" }, 
        ["_"] = { "trim_whitespace" },
      },
      
      -- Configuración de "Formatear al Guardar"
      format_on_save = {
        lsp_fallback = true, -- Si no hay formateador (ej. prettier), usa el LSP
        async = false,       -- Bloquear hasta que termine (evita condiciones de carrera)
        timeout_ms = 1000,   -- Tiempo máximo de espera
      },
    })

    -- Atajo de teclado manual por si quieres formatear sin guardar
    vim.keymap.set({ "n", "v" }, "<leader>mp", function()
      conform.format({
        lsp_fallback = true,
        async = false,
        timeout_ms = 1000,
      })
    end, { desc = "Formatear archivo o rango (Make Pretty)" })
  end,
}

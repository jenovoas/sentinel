return {
  "mfussenegger/nvim-dap",
  dependencies = {
    -- Plugins para adaptadores de depuración específicos
    -- Por ejemplo, para Python:
    -- "mfussenegger/nvim-dap-python",
    -- Para Typescript/Javascript:
    -- "mxsdev/nvim-dap-vscode-js",

    -- UI para DAP
    "rcarriga/nvim-dap-ui",
    -- Utilidades para la configuración de DAP
    "theHamsta/nvim-dap-virtual-text",
    "nvim-neotest/nvim-nio", -- Required by nvim-dap-ui
  },
  config = function()
    local dap = require("dap")
    local dapui = require("dapui")

    -- Configuración básica de DAP UI
    dapui.setup({
      expanded = true, -- Auto-expand the UI
      elements = {
        -- Puedes personalizar la disposición de los elementos aquí
        -- Por ejemplo:
        -- {
        --   id = "scopes",
        --   size = 0.25,
        -- },
        -- {
        --   id = "breakpoints",
        --   size = 0.25,
        -- },
        -- {
        --   id = "stack",
        --   size = 0.25,
        -- },
        -- {
        --   id = "watches",
        --   size = 0.25,
        -- },
      },
      layouts = {
        {
          elements = {
            { id = "scopes", size = 0.30 },
            { id = "breakpoints", size = 0.20 },
            { id = "stacks", size = 0.25 },
            { id = "watches", size = 0.25 },
          },
          size = 0.40, -- Altura total de la ventana DAP UI
          position = "right", -- Posición de la ventana DAP UI (right, left, top, bottom)
        },
      },
    })

    -- Eventos para abrir y cerrar DAP UI automáticamente
    dap.listeners.after.event_initialized["dapui_config"] = function()
      dapui.open()
    end
    dap.listeners.before.event_terminated["dapui_config"] = function()
      dapui.close()
    end
    dap.listeners.before.event_exited["dapui_config"] = function()
      dapui.close()
    end

    -- Mapeos de teclado básicos para DAP (puedes mover esto a keymaps.lua si prefieres)
    vim.keymap.set("n", "<leader>dc", function() dap.continue() end, { desc = "DAP Continue" })
    vim.keymap.set("n", "<leader>dr", function() dap.repl.toggle() end, { desc = "DAP REPL Toggle" })
    vim.keymap.set("n", "<leader>dt", function() dap.toggle_breakpoint() end, { desc = "DAP Toggle Breakpoint" })
    vim.keymap.set("n", "<leader>dcr", function() dap.clear_breakpoints() end, { desc = "DAP Clear Breakpoints" })
    vim.keymap.set("n", "<leader>ds", function() dap.step_over() end, { desc = "DAP Step Over" })
    vim.keymap.set("n", "<leader>di", function() dap.step_into() end, { desc = "DAP Step Into" })
    vim.keymap.set("n", "<leader>du", function() dap.step_out() end, { desc = "DAP Step Out" })
    vim.keymap.set("n", "<leader>do", function() dapui.open({}) end, { desc = "DAP UI Open" })
    vim.keymap.set("n", "<leader>dq", function() dapui.close({}) end, { desc = "DAP UI Close" })
    vim.keymap.set("n", "<leader>dx", function() dap.terminate() end, { desc = "DAP Terminate" })
    vim.keymap.set("n", "<leader>drc", function() dap.run_to_cursor() end, { desc = "DAP Run to Cursor" })

    -- Aquí deberás añadir las configuraciones de los adaptadores de depuración (DAP)
    -- por ejemplo, para Python:
    -- require("dap-python").setup("/usr/bin/python")
    -- para js:
    -- require("dap-vscode-js").setup({
    --   -- node_path = "node", --  donde se encuentra su ejecutable Node.js
    --   -- debugger_path = "(rute to vscode-js debug adapter)", --  la ruta a vscode-js debug adapter
    --   -- You will need to get the debug adapter itself:
    --   -- `npm install -g vscode-js-debug`
    --   -- or `yarn global add vscode-js-debug`
    -- })
    -- Luego, puedes activar los adaptadores. Por ejemplo:
    -- dap.configurations.javascript = { require("dap-vscode-js").get_configuration(nil, { type = "node" }) }
    -- dap.configurations.typescript = { require("dap-vscode-js").get_configuration(nil, { type = "node" }) }
  end,
}

-- lua/plugins/editor.lua
return {
  -- === TELESCOPE (El Buscador) ===
  {
    "nvim-telescope/telescope.nvim",
    tag = "0.1.6",
    dependencies = { "nvim-lua/plenary.nvim" },
    keys = {
      -- Atajos de teclado para buscar
      { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "Buscar Archivos (Files)" },
      { "<leader>fg", "<cmd>Telescope live_grep<cr>", desc = "Buscar Texto (Grep)" },
      { "<leader>fb", "<cmd>Telescope buffers<cr>", desc = "Buscar Buffers abiertos" },
      { "<leader>fh", "<cmd>Telescope help_tags<cr>", desc = "Ayuda de Neovim" },
      -- Buscar en los archivos de configuración de Neovim
      { "<leader>fn", "<cmd>Telescope find_files cwd=~/.config/nvim<cr>", desc = "Archivos de Config" },
    },
            config = function()
              local telescope = require("telescope")
              telescope.setup({
                defaults = {
                  file_ignore_patterns = { "node_modules", ".git" }, -- Ignorar carpetas pesadas
                  vimgrep_arguments = {
                    "rg", "--color=never", "--no-heading", "--with-filename",
                    "--line-number", "--column", "--smart-case"
                  },
                },
                pickers = {
                  find_files = {
                    hidden = true, -- Buscar archivos ocultos (dotfiles)
                  },
                },
              })
            end,
          },  -- === NEO-TREE (Explorador de Archivos Lateral) ===
  -- Si vienes de LazyVim, estás acostumbrado a ver tus archivos a la izquierda.
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons", -- Iconos de carpetas
      "MunifTanjim/nui.nvim",
    },
    keys = {
      { "<leader>e", "<cmd>Neotree toggle<cr>", desc = "Abrir/Cerrar Explorador" },
    },
    config = function()
      require("neo-tree").setup({
        filesystem = {
          filtered_items = {
            visible = true, -- Ver archivos ocultos (empiezan con punto)
            hide_dotfiles = false,
            hide_gitignored = false,
          },
          follow_current_file = {
            enabled = true, -- Enfocar el archivo que estás editando en el árbol
          },
        },
        window = {
          width = 30, -- Ancho del panel
          mappings = {
            ["<space>"] = "none", -- Desactivar espacio en el árbol para no conflictos
          },
        },
      })
    end,
  }
}

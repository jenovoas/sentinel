-- lua/plugins/bufferline.lua
return {
  'akinsho/bufferline.nvim',
  version = "*",
  dependencies = { 'nvim-tree/nvim-web-devicons' },
  event = "BufReadPost", -- Carga después de leer un buffer
  config = function()
    require("bufferline").setup({
      options = {
        mode = "buffers", -- Muestra solo buffers abiertos
        numbers = "ordinal", -- Muestra números de orden secuenciales (1, 2, 3...)
        -- Siempre muestra el búfer actual al principio si hay muchos
        always_show_bufferline = true, 
        themable = true, -- Permite que el tema de Neovim lo afecte
        color_icons = true, -- Mostrar iconos de colores para los tipos de archivo
        offsets = { {
          filetype = "NvimTree",
          text = "File Explorer",
          text_align = "left",
          separator = true
        } },
        diagnostics = "nvim_lsp", -- Muestra diagnósticos de LSP
        diagnostics_indicator = function(count, level, diagnostics_dict, context)
          local icon = level:match("error") and " " or " "
          return " " .. icon .. count
        end,
        show_buffer_close_icons = true, -- Mostrar icono de cerrar en cada búfer
        show_close_icon = true, -- Mostrar icono de cerrar en la propia bufferline
        show_tab_indicators = true,
        -- Puedes configurar un tema personalizado aquí o usar el tema de Neovim
        -- theme = "monokai_pro", 
      },
    })
  end,
}

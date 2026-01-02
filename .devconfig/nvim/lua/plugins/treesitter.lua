-- lua/plugins/treesitter.lua
return {
  {
    "nvim-treesitter/nvim-treesitter",
    branch = "master",
    build = ":TSUpdate", -- Actualiza los parsers al instalar
    event = { "BufReadPost", "BufNewFile" }, -- Carga perezosa al abrir archivos
    config = function()
      require("nvim-treesitter.configs").setup({
        -- Añado los lenguajes más comunes. Puedes añadir más a la lista.
        ensure_installed = { 
          "bash", "c", "html", "javascript", "json", "lua", "luadoc", 
          "markdown", "markdown_inline", "python", "query", "regex", 
          "tsx", "typescript", "vim", "vimdoc", "yaml", "css"
        },
        
        -- Instalación automática si abres un archivo de un lenguaje que no tienes
        auto_install = true,

        -- Resaltado de sintaxis (¡Esto es lo importante!)
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false, -- Desactiva el motor viejo de vim
        },

        -- Identación basada en treesitter (Suele ser mejor que la nativa)
        indent = { enable = true },
      })
    end,
  }
}

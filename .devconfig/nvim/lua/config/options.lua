-- lua/config/options.lua
local opt = vim.opt

opt.number = true          -- Muestra números de línea
opt.relativenumber = true  -- Números relativos (útil para saltos)
opt.tabstop = 2            -- Tamaño del tab (ajusta a 4 si prefieres)
opt.shiftwidth = 2
opt.expandtab = true       -- Usa espacios en lugar de tabs
opt.smartindent = true
opt.wrap = false           -- No ajustar líneas largas
opt.ignorecase = true      -- Búsqueda insensible a mayúsculas
opt.smartcase = true       -- ...a menos que uses una mayúscula
opt.cursorline = true      -- Resalta la línea actual
opt.termguicolors = true   -- Colores verdaderos
opt.scrolloff = 8          -- Mantiene 8 líneas arriba/abajo al scrollear
opt.clipboard = "unnamedplus" -- Sincroniza con el portapapeles del sistema

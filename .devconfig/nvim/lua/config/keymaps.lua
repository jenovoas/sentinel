-- 1. Definir la tecla Leader como ESPACIO
-- Es crucial definir esto ANTES de cualquier plugin
vim.g.mapleader = " "
vim.g.maplocalleader = " "

local map = vim.keymap.set

-- === GUARDADO CON CTRL+S (NUEVO) ===
-- Guarda en modo Normal, Insertar y Visual.
-- <cmd>w<cr> guarda y <esc> asegura que vuelvas al modo normal (confirmación visual)
map({ "n", "i", "v" }, "<C-s>", "<cmd>w<cr><esc>", { desc = "Guardar archivo" })


-- === GENERAL ===

-- Mejor guardado y salida (más rápido que escribir :w<Enter>)
map("n", "<leader>w", "<cmd>w<cr>", { desc = "Guardar archivo" })
map("n", "<leader>q", "<cmd>q<cr>", { desc = "Salir" })

-- Limpiar el resaltado de búsqueda con ESC
-- (Por defecto nvim mantiene lo que buscaste resaltado por siempre)
map("n", "<Esc>", "<cmd>nohlsearch<CR>", { desc = "Limpiar resaltado" })

-- === NAVEGACIÓN DE VENTANAS (Splits) ===
-- Usa Control + h/j/k/l para moverte entre ventanas (como en LazyVim)
map("n", "<C-h>", "<C-w>h", { desc = "Ir a la ventana izquierda" })
map("n", "<C-j>", "<C-w>j", { desc = "Ir a la ventana inferior" })
map("n", "<C-k>", "<C-w>k", { desc = "Ir a la ventana superior" })
map("n", "<C-l>", "<C-w>l", { desc = "Ir a la ventana derecha" })

-- Redimensionar ventanas con flechas (Opcional, pero útil)
map("n", "<C-Up>", "<cmd>resize +2<cr>", { desc = "Aumentar altura ventana" })
map("n", "<C-Down>", "<cmd>resize -2<cr>", { desc = "Reducir altura ventana" })
map("n", "<C-Left>", "<cmd>vertical resize -2<cr>", { desc = "Reducir ancho ventana" })
map("n", "<C-Right>", "<cmd>vertical resize +2<cr>", { desc = "Aumentar ancho ventana" })

-- === BUFFERS ===
-- Navegar entre buffers abiertos con Shift + h/l
map("n", "<S-h>", "<cmd>bprevious<cr>", { desc = "Buffer anterior" })
map("n", "<S-l>", "<cmd>bnext<cr>", { desc = "Buffer siguiente" })
map("n", "<leader>bd", "<cmd>bdelete<cr>", { desc = "Cerrar Buffer actual" })

-- === BUFFERLINE ===
map("n", "<leader>bn", "<cmd>BufferLineCycleNext<CR>", { desc = "Siguiente Buffer (BufferLine)" })
map("n", "<leader>bp", "<cmd>BufferLineCyclePrev<CR>", { desc = "Buffer Anterior (BufferLine)" })
map("n", "<leader>bb", "<cmd>lua require('fzf-lua').buffers()<CR>", { desc = "Seleccionar Buffer (Fzf-Lua)" })

-- === NAVEGACIÓN DIRECTA DE BUFFERS (1-9) ===
-- Permite saltar directamente a un búfer por su número en la bufferline
for i = 1, 9 do
  map("n", "<leader>b" .. i, "<cmd>BufferLineGoToBuffer " .. i .. "<CR>", { desc = "Ir al Buffer " .. i })
end


-- === EDICIÓN ===

-- Mover líneas seleccionadas arriba/abajo (¡Súper útil!)
-- Esto imita el comportamiento de VSCode de mover bloques de código con Alt+Flechas
map("v", "J", ":m '>+1<CR>gv=gv", { desc = "Mover bloque abajo" })
map("v", "K", ":m '<-2<CR>gv=gv", { desc = "Mover bloque arriba" })

-- Mantener la selección al identar
-- Normalmente al hacer < o > pierdes la selección. Esto lo arregla.
map("v", "<", "<gv", { desc = "Identar izquierda (mantiene selección)" })
map("v", ">", ">gv", { desc = "Identar derecha (mantiene selección)" })

-- Pegar sin perder lo copiado
-- Cuando pegas sobre un texto seleccionado en Vim, por defecto pierdes lo que tenías
-- en el portapapeles. Esto evita eso al pegar con 'p'.
map("x", "<leader>p", [["_dP]], { desc = "Pegar sin sobreescribir registro" })

-- === UTILIDADES ===

-- Copiar al portapapeles del sistema con <leader>y
map({"n", "v"}, "<leader>y", [["+y]], { desc = "Copiar al sistema" })
map("n", "<leader>Y", [["+Y]], { desc = "Copiar línea al sistema" })

--
-- === AI / AVANTE ===
map("n", "<leader>ac", "<cmd>AvanteChat<CR>", { desc = "Avante: Iniciar Chat" })
map("n", "<leader>ag", "<cmd>AvanteGenerate<CR>", { desc = "Avante: Generar con Prompt" })
map("v", "<leader>ac", "<cmd>AvanteChatVisual<CR>", { desc = "Avante: Chatear con Selección" })
map("v", "<leader>ag", "<cmd>AvanteGenerateVisual<CR>", { desc = "Avante: Generar con Selección" })

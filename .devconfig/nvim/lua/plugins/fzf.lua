-- lua/plugins/fzf.lua
return {
	"ibhagwan/fzf-lua",
	dependencies = { "nvim-tree/nvim-web-devicons" },
	config = function()
		local fzf = require("fzf-lua")

		fzf.setup({
			winopts = {
				height = 0.85,
				width = 0.80,
				preview = {
					layout = "flex",
					flip_columns = 120,
				},
			},
			-- === AQUÍ CONFIGURAMOS HJKL PARA MOVERSE ===
			keymap = {
				builtin = {
					-- Moverse en la lista de resultados de Neovim
					["<C-j>"] = "down",
					["<C-k>"] = "up",
				},
				fzf = {
					-- Moverse dentro del proceso interno de fzf
					["ctrl-j"] = "down",
					["ctrl-k"] = "up",
					["ctrl-q"] = "select-all+accept", -- Enviar todo a quickfix
				},
			},
		})

		-- === TUS ATAJOS DE TECLADO ===
		-- Buscar Archivos (Leader + Space)
		vim.keymap.set("n", "<leader><space>", fzf.files, { desc = "Buscar Archivos (Fzf)" })
		-- Buscar Texto (Grep)
		vim.keymap.set("n", "<leader>/", fzf.live_grep, { desc = "Buscar Texto (Grep)" })
		-- Buffers
		vim.keymap.set("n", "<leader>,", fzf.buffers, { desc = "Cambiar Buffer" })
		-- Archivos Recientes
		vim.keymap.set("n", "<leader>fr", fzf.oldfiles, { desc = "Archivos Recientes" })
	end,
}

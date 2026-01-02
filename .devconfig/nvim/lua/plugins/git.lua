-- lua/plugins/git.lua
return {
	"lewis6991/gitsigns.nvim",
	event = { "BufReadPre", "BufNewFile" },
	config = function()
		require("gitsigns").setup({
			-- Ver quién editó la línea actual (como en VSCode con GitLens)
			current_line_blame = true,
			current_line_blame_opts = {
				delay = 500, -- Esperar medio segundo antes de mostrar el mensaje
			},
			-- Personalización de los signos en la barra izquierda
			signs = {
				add = { text = "┃" },
				change = { text = "┃" },
				delete = { text = "_" },
				topdelete = { text = "‾" },
				changedelete = { text = "~" },
			},
		})

		-- Atajos útiles para Git
		vim.keymap.set("n", "<leader>gb", ":Gitsigns toggle_current_line_blame<CR>", { desc = "Toggle Git Blame" })
		vim.keymap.set("n", "<leader>gp", ":Gitsigns preview_hunk<CR>", { desc = "Ver qué cambió en este bloque" })
	end,
}

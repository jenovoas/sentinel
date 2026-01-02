return {
  {
    "folke/snacks.nvim",
    opts = {
      dashboard = {
        preset = {
          -- 1. TU ARTE ASCII (Pegalo dentro de los corchetes)
          header = [[

    /$$$$$ /$$   /$$                                          /$$$$$$
   |__  $$| $$$ | $$                                         /$$__  $$
      | $$| $$$$| $$  /$$$$$$  /$$    /$$ /$$$$$$   /$$$$$$ | $$  \__/
      | $$| $$ $$ $$ /$$__  $$|  $$  /$$//$$__  $$ |____  $$|  $$$$$$
 /$$  | $$| $$  $$$$| $$  \ $$ \  $$/$$/| $$  \ $$  /$$$$$$$ \____  $$
| $$  | $$| $$\  $$$| $$  | $$  \  $$$/ | $$  | $$ /$$__  $$ /$$  \ $$
|  $$$$$$/| $$ \  $$|  $$$$$$/   \  $/  |  $$$$$$/|  $$$$$$$|  $$$$$$/
 \______/ |__/  \__/ \______/     \_/    \______/  \_______/ \______/

     ]],

          -- 2. AQUÍ ESTÁ EL ARREGLO DE LOS BOTONES
          -- Definimos explícitamente qué hace cada tecla
          keys = {
            { icon = " ", key = "f", desc = "Buscar Archivo", action = ":lua Snacks.dashboard.pick('files')" },
            { icon = " ", key = "n", desc = "Nuevo Archivo", action = ":ene | startinsert" },
            { icon = " ", key = "r", desc = "Archivos Recientes", action = ":lua Snacks.dashboard.pick('oldfiles')" },
            { icon = " ", key = "g", desc = "Buscar Texto", action = ":lua Snacks.dashboard.pick('live_grep')" },
            { icon = " ", key = "c", desc = "Configuración", action = ":lua Snacks.dashboard.pick('files', {cwd = vim.fn.stdpath('config')})" },

            -- ESTA ES LA QUE NO HACÍA NADA:
            { icon = "💤 ", key = "l", desc = "Lazy (Plugins)", action = ":Lazy" },

            { icon = " ", key = "q", desc = "Salir", action = ":qa" },
          },
        },
      },
    },
  },
}

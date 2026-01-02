-- lua/plugins/cmp.lua
return {
  -- nvim-cmp: El motor de autocompletado
  'hrsh7th/nvim-cmp',
  event = 'InsertEnter', -- Cargar solo al entrar en modo inserción
  dependencies = {
    -- Snippets
    'L3MON4D3/LuaSnip', -- Motor de snippets
    'saadparwaiz1/cmp_luasnip', -- Integración de nvim-cmp con LuaSnip
    'rafamadriz/friendly-snippets', -- Colección de snippets comunes

    -- Fuentes para nvim-cmp
    'hrsh7th/cmp-nvim-lsp',   -- Fuente de autocompletado para LSP
    'hrsh7th/cmp-buffer',     -- Fuente de autocompletado para el buffer actual
    'hrsh7th/cmp-path',       -- Fuente de autocompletado para rutas de archivos
    'hrsh7th/cmp-cmdline',    -- Fuente de autocompletado para la línea de comandos de Neovim
    'onsails/lspkind.nvim',   -- Iconos para autocompletado
  },
  config = function()
    local cmp = require('cmp')
    local luasnip = require('luasnip')

    -- Cargar todos los snippets de friendly-snippets
    require('luasnip.loaders.from_vscode').lazy_load()

    cmp.setup({
      snippet = {
        expand = function(args)
          luasnip.lsp_expand(args.body) -- Expande snippets con LSP
        end,
      },
      mapping = cmp.mapping.preset.insert({
        ['<C-b>'] = cmp.mapping.scroll_docs(-4),
        ['<C-f>'] = cmp.mapping.scroll_docs(4),
        ['<C-Space>'] = cmp.mapping.complete(), -- Activar autocompletado
        ['<C-e>'] = cmp.mapping.abort(),        -- Cerrar ventana de autocompletado
        ['<CR>'] = cmp.mapping.confirm({ select = true }), -- Confirmar selección
        -- Moverse entre sugerencias con <Tab> y <S-Tab>
        ['<Tab>'] = cmp.mapping(function(fallback)
          if cmp.visible() then
            cmp.select_next_item()
          elseif luasnip.expand_or_jumpable() then
            luasnip.expand_or_jump()
          else
            fallback()
          end
        end, { 'i', 's' }),
        ['<S-Tab>'] = cmp.mapping(function(fallback)
          if cmp.visible() then
            cmp.select_prev_item()
          elseif luasnip.jumpable(-1) then
            luasnip.jump(-1)
          else
            fallback()
          end
        end, { 'i', 's' }),
      }),
      sources = cmp.config.sources({
        { name = 'nvim_lsp' },    -- Sugerencias del servidor de lenguaje
        { name = 'avante' },      -- Sugerencias de Avante
        { name = 'luasnip' },     -- Sugerencias de snippets
        { name = 'buffer' },      -- Sugerencias del contenido del buffer
        { name = 'path' },        -- Sugerencias de rutas de archivos
      }),
      window = {
        completion = cmp.config.window.bordered(),
        documentation = cmp.config.window.bordered(),
      },
      formatting = {
        format = require('lspkind').cmp_format({
          maxwidth = 50, -- Ancho máximo para el texto
          ellipsis_char = '...', -- Caracter para truncar
        }),
      },
    })

    -- Configuración específica para autocompletado en la línea de comandos
    cmp.setup.cmdline(':', {
      mapping = cmp.mapping.preset.cmdline(),
      sources = cmp.config.sources({
        { name = 'cmdline' }
      })
    })
  end,
}

#!/bin/bash
# Poblar whitelist usando bpftool con flag correcto

echo "🔐 Poblando whitelist del eBPF LSM (v2)..."
echo "======================================"

# Comandos básicos permitidos (Paths completos requeridos por el nuevo eBPF)
COMMANDS=(
    "/usr/bin/bash"
    "/usr/bin/sh"
    "/usr/bin/zsh"
    "/bin/zsh"
    "/usr/bin/tmux"
    "/usr/bin/bash"
    "/bin/bash"
    "/usr/bin/sh"
    "/bin/sh"
    "/usr/bin/cp"
    "/bin/cp"
    "/bin/ls"
    "/usr/bin/ls"
    "/usr/bin/cat"
    "/usr/bin/nvim"
    "/usr/bin/dmesg"
    "/usr/local/bin/nvim"
    "/usr/bin/vim"
    "/usr/bin/nano"
    "/usr/bin/pwd"
    "/usr/bin/date"
    "/usr/bin/sudo"
    "/usr/bin/bpftool"
    "/usr/sbin/bpftool"
    "/usr/bin/rm"
    "/usr/sbin/rm"
    "/usr/bin/ps"
    "/usr/bin/grep"
    "/usr/bin/awk"
    "/usr/bin/sed"
    "/usr/bin/python3"
    "/usr/bin/make"
    "/usr/bin/clang"
    "/usr/bin/llvm-strip"
    "/usr/bin/git"
    "/usr/bin/eza"
    "/usr/bin/mkdir"
    "/usr/bin/cp"
    "/usr/bin/mv"
    "/usr/bin/touch"
    "/usr/bin/chmod"
    "/usr/bin/chown"
    "/usr/bin/clear"
    "/usr/bin/tput"
    "/usr/bin/sort"
    "/usr/bin/uniq"
    "/usr/bin/head"
    "/usr/bin/tail"
    "/usr/bin/xxd"
    "/usr/sbin/ip"
    "/usr/sbin/ss"
    "/usr/local/bin/starship"  # Shell prompt
    "/usr/sbin/unix_chkpwd"    # Required for sudo auth
    "/usr/bin/id"
    "/usr/bin/whoami"
    "/usr/bin/dirname"
    "/usr/bin/wc"
    "/usr/bin/cut"
    "/usr/bin/env"
    "/usr/bin/sleep"
    "/bin/true"               # Required for testing
    "/usr/bin/true"           # Required for testing
    "/usr/bin/find"           # Useful utility
    "/usr/bin/xargs"          # Useful utility
    "/usr/bin/nawk"           # Used by starship/shell plugins
    "/tmp/malicious_attack_tool" # FOR POC: Whitelisted but Semantic Blocked
    "/usr/lib/git-core/git-remote-https" # Required for git push
    "/usr/lib/git-core/git"   # Internal git binary
    "/usr/lib/git-core/git-credential-store" # Required to save password
    "/usr/libexec/sudo/sudoers.so" # Sudo internal modules
    # Shell & desktop utilities to prevent annoyance
    "/usr/bin/mkfifo"
    "/usr/bin/dircolors"
    "/usr/bin/zoxide"
    "/usr/bin/fzf"
    "/usr/bin/mawk"
    "/usr/bin/lesspipe"
    "/usr/bin/basename"
    "/usr/local/bin/ollama"
)

# Ruta del map pinned (establecida por load.sh)
MAP_PATH="/sys/fs/bpf/guardian_alpha/whitelist_map"

if [ ! -f "$MAP_PATH" ]; then
    echo "❌ Error: No se encontró el map en $MAP_PATH"
    echo "💡 ¿Has ejecutado 'sudo bash ebpf/load.sh' primero?"
    exit 1
fi

echo "✅ Map encontrado en: $MAP_PATH"
echo ""

# Poblar con comandos
for cmd in "${COMMANDS[@]}"; do
    # Generar key de 256 bytes (zero-padded) en formato hex con espacios
    # Esto asegura compatibilidad con char[256] y bpftool parsing
    key_hex=$(python3 -c "import sys; cmd=sys.argv[1].encode(); print(' '.join(f'{b:02x}' for b in cmd.ljust(256, b'\0')))" "$cmd")

    # Valor: 01 (allowed) - 1 byte para __u8
    value_hex="01"

    # Intentar agregar usando el path pinned
    sudo bpftool map update pinned "$MAP_PATH" \
        key hex $key_hex \
        value hex $value_hex \
        any

    if [ $? -eq 0 ]; then
        echo "✅ $cmd"
    else
        echo "❌ Falló: $cmd"
    fi
done

echo ""
echo "======================================"
echo "✅ Intentado poblar ${#COMMANDS[@]} comandos"
echo ""
echo "📊 Verificar contenido del map:"
echo "   sudo bpftool map dump pinned $MAP_PATH"

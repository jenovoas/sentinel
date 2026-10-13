# OmniRoute — Bridge MCP stdio→http en el fan

Procedimiento operativo (para no re-descubrirlo cada sesión).

## Topología
- **OmniRoute corre en la LAPTOP** (`localhost:20128`, `0.0.0.0:20128`). No corre en el fan.
- **Fan** = `157.254.174.40:4222`, usuario `jnovoas`, `ssh fan` (key `~/.ssh/id_ed25519_server`).
- El fan NO alcanza la LAN de la laptop, así que se abre un **túnel reverso** desde la laptop al fan que lleva el `:20128` de la laptop hacia `127.0.0.1:20128` del fan.
- En el fan vive un **bridge MCP stdio→http** que habla con ese `127.0.0.1:20128` (vía túnel) usando el MCP streamable-http de omniroute.

## Componentes ya desplegados (verificados 2026-08-07)
1. **Túnel** (en la laptop, systemd user):
   - Unit: `~/.config/systemd/user/fan-omniroute-tunnel.service`
   - Comando: `autossh -M 0 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes -N -R 20128:127.0.0.1:20128 fan`
   - Estado: `systemctl --user is-active fan-omniroute-tunnel.service` → `active`. Auto-arranca (WantedBy=default.target).
2. **Bridge MCP** (en el fan):
   - Binario: `/home/jnovoas/.local/bin/omniroute_mcp_bridge.py` (ejecutable).
   - Protocolo: stdio (JSON-RPC) → `http://127.0.0.1:20128/api/mcp/stream` (streamable-http).
   - Auth MCP = cookie de dashboard omniroute (NO API key). El bridge hace login (`/api/auth/login`, pass `darkfenix`) y re-login si la cookie expira. Usa `http.cookiejar` (MozillaCookieJar en `/tmp/omni_cookies_fan_bridge.txt`).
   - Reenvía `initialize` al server para obtener el `mcp-session-id` real (va en header de cada llamada siguiente).
   - **NO toca omniroute**: solo delega.

## Verificación punta a punta (desde el fan)
```bash
ssh fan
cat > /tmp/bt.py <<'PY'
import subprocess, json
p = subprocess.Popen(["python3","/home/jnovoas/.local/bin/omniroute_mcp_bridge.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
def send(o): p.stdin.write(json.dumps(o)+"\n"); p.stdin.flush()
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}})
print("INIT:", p.stdout.readline().strip()[:160])
send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
for _ in range(60):
    l=p.stdout.readline()
    if not l: break
    l=l.strip()
    if not l: continue
    try: d=json.loads(l)
    except: continue
    if d.get("id")==2 and "result" in d:
        print("TOOLS:", len(d["result"].get("tools",[]))); break
p.terminate()
PY
python3 /tmp/bt.py
# Esperado: TOOLS: 107 (omniroute_list_combos, omniroute_test_combo, omniroute_check_quota, ...)
```

## Para consumir el bridge desde Hermes
Hermes solo soporta MCP **stdio** (`mcp_servers:` → `command:`). Donde corra Hermes, registrar:
```yaml
mcp_servers:
  omniroute-fan:
    command: /home/jnovoas/.local/bin/omniroute_mcp_bridge.py
    enabled: true
```
NOTA: en el fan NO hay Hermes (`~/.hermes` no existe). El bridge queda listo como binario consumible; enchufarlo donde corresponda.

## Pitfalls
- El MCP de omniroute es **streamable-http con cookie de dashboard**, NO API key. `omniroute --mcp` (stdio nativo) **crasha** en esta instalación → por eso existe el bridge.
- El túnel es reverso (`-R`): se abre DESDE la laptop. Si la laptop está apagada, el fan pierde el 20128.
- No reconstruir nada de esto "porque parece roto" — verificar estado primero con los comandos arriba.

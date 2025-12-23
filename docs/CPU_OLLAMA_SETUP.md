# CPU-only Ollama Deployment 🔧

This document explains how to deploy Sentinel with a CPU-only Ollama model and open the frontend in your browser.

## 1) Requirements

- Docker Engine and Docker Compose (v2+) installed
- At least a few GB of RAM and enough disk to store models
- (Optional) `curl` installed for simple health checks

## 2) Configuration

- Ensure `.env` contains:

```
AI_ENABLED=true
OLLAMA_MODEL=phi3:mini
OLLAMA_CPU_ONLY=true
OLLAMA_URL=http://ollama:11434
```

`phi3:mini` is a compact model that runs on CPU; change if you prefer another CPU-compatible model. `OLLAMA_CPU_ONLY` is informational and used by scripts to indicate no GPU-specific settings are required.

## 3) Start the service (recommended)

Use the provided scripts:

- Linux / macOS:

```bash
./scripts/start-cpu-ollama.sh
```

- Windows (PowerShell):

```powershell
.\scripts\start-cpu-ollama.ps1
```

These scripts start the Docker stack with the `ai` profile (`docker compose --profile ai up -d --build`), wait for Ollama and the backend to be reachable, and open the frontend at `http://localhost:3000`.

## 4) Manual commands (alternate)

To just start the AI services:

```bash
docker compose --profile ai up -d --build ollama ollama-init
```

To start the full stack:

```bash
docker compose --profile ai up -d --build
```

## 5) Verify

- Ollama reachable: `curl -v http://localhost:11434/api/tags`
- Backend health: `curl -v http://localhost:8000/health` (returns JSON)
- Frontend: open `http://localhost:3000`
- Quick AI test: `./scripts/test-ollama.sh` (Linux/macOS) or `scripts\test-ollama.ps1` (Windows)

## 6) Troubleshooting

- If model downloads are slow, inspect logs: `docker compose logs -f ollama-init`
- If Ollama is not reachable, try `docker compose ps` to ensure the container is running and port `11434` is published
- If you have a GPU and intend to use it, make sure NVIDIA container toolkit drivers are installed and the GPU-specific instructions are followed (see `docs/OLLAMA_GPU_SETUP.md`)

---

If you want, I can add a `Makefile` target or add systemd service files to run Ollama persistently; tell me your preferred OS for production and I'll prepare them.
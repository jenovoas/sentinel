# 🦅 Sentinel Vault - v1.0 Production Deployment

**Architecture**: Docker Compose with Nginx Reverse Proxy (SSL Termination).

---

## 🚀 Deployment Steps

### 1. Prerequisites
- Docker & Docker Compose
- Ports 80, 443, 3000, 8000 available.

### 2. Quick Start
```bash
# 1. Generate SSL Certificates (Self-Signed for Localhost)
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/certs/nginx.key \
    -out nginx/certs/nginx.crt \
    -subj "/CN=localhost"

# 2. Start the Stack
docker-compose up -d --build

# 3. Access
# Secure HTTPS Access
https://localhost

# (Accept self-signed certificate warning in browser)
```

### 3. Services Verification
- **Frontend**: `https://localhost` (Proxy -> Port 3000)
- **Backend API**: `https://localhost/api/docs` (Proxy -> Port 8000)
- **Direct Access**: `http://localhost:3000` (Still available for debug if needed)

### 4. Production Hardening Checklist
- [x] **Containerization**: Backend & Frontend isolated.
- [x] **Network**: Backend not exposed publicly (only via Nginx).
- [x] **Encryption**: Traffic encrypted via TLS 1.2/1.3.

---

**Top Secret**: The `nginx.key` is generated locally and never stored in git.

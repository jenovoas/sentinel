#  Sentinel Cortex - Changelog

## [Unreleased] - 2025-12-30

### 🔧 Fixed
- **Docker Configuration**
  - Removed obsolete `version: '3.8'` syntax from docker-compose files
  - Fixed frontend build context from `./frontend/poc` to `./frontend`
  - Updated backend healthcheck endpoint to `/health`
  - Moved hardcoded passwords to environment variables

### 🔒 Security
- **Credentials Management**
  - Generated 6 cryptographically secure passwords using Python secrets module
  - Created `.env` file with secure credentials (POSTGRES_PASSWORD, SECRET_KEY, etc.)
  - Moved all sensitive data from docker-compose to environment variables
  - Created backup of original .env file

###  Added
- **Frontend**
  - Switched from Sentinel Vault POC to Executive Dashboard as default frontend
  - Backed up Trinity GUI to `app-trinity-backup/`
  - Backed up Crypto Wallet POC to `poc-vault-backup/`
  - Removed WASM dependencies causing build failures

### 📝 Documentation
- Created comprehensive session summary
- Added Docker diagnostics report
- Documented all applied fixes
- Created credentials reference document
- Updated stack status documentation

### 🐛 Bug Fixes
- Fixed PostgreSQL password authentication by recreating volume with new credentials
- Removed problematic WASM modules (`wasm-test`, `wasm-loader.ts`)
- Fixed frontend build failures due to missing dependencies

### 🏗 Infrastructure
- **Stack Status**: All 5 services running successfully
  - PostgreSQL: Healthy on port 5432
  - Redis: Healthy on port 6379
  - Backend API: Running on port 8000
  - Frontend: Running on port 3000
  - Node Exporter: Running on port 9100

---

## Previous Releases

See [CHANGELOG.md](CHANGELOG.md) for full history.

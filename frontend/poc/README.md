# Sentinel Vault POC - Frontend

## Setup

```bash
# 1. Install dependencies
cd frontend/poc
npm install

# 2. Start dev server
npm run dev
```

## Access

- 🌐 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000

## Features

### 1. Password Vault
- Unlock with master password
- Save encrypted passwords
- List all services
- Retrieve passwords (decrypted)

### 2. Password Analysis (Ollama)
- Real-time strength analysis
- Pattern detection (pet names, years, etc.)
- Suggestions for improvement
- Visual score indicator

### 3. Crypto Wallet
- Generate HD wallet (Bitcoin + Ethereum)
- Display seed phrase (⚠️ show only once)
- Recover wallet from seed phrase
- Show addresses for both chains

### 4. Benchmarks
- Encryption performance metrics
- Ollama analysis latency
- Real-time results

## Usage

1. **Start backend first**:
   ```bash
   cd backend/poc
   python main.py
   ```

2. **Start frontend**:
   ```bash
   cd frontend/poc
   npm run dev
   ```

3. **Open browser**: http://localhost:3000

4. **Enter master password** (any password for POC)

5. **Test features**:
   - Save a password
   - Analyze password strength
   - Generate crypto wallet
   - Run benchmarks

## Tech Stack

- **Next.js 14** (App Router)
- **React** (Client components)
- **Tailwind CSS** (Styling)
- **Fetch API** (Backend communication)

## Notes

- ⚠️ This is a POC - data is stored in memory only
- ⚠️ Seed phrases shown in UI (in production, show only once)
- ⚠️ No authentication (in production, use JWT/sessions)
- ✅ Fully functional for demo purposes

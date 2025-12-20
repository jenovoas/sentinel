# 💰 Phase 6: Financial Dashboard - Privacy First

**Objetivo**: Unificar Crypto y Finanzas Tradicionales en un solo dashboard.
**Diferenciador**: Privacidad absoluta. Tus datos financieros nunca salen de tu máquina. Cifrado AES-256 local.

---

## 🏗️ Architecture

### **1. Data Model (Local & Encrypted)**
*   **Assets**: Criptomonedas (Live Sync) y Activos Manuales (Cash, Real Estate, Stocks).
*   **Transactions**: Historial unificado.
*   **Privacy**: Base de datos SQLite cifrada (SQLCipher logic o AES en columnas).

### **2. Backend (`finance_service.py`)**
*   **Aggregation**: Combina datos del `CryptoService` con datos manuales.
*   **Price Feeds**:
    *   Crypto: Ya tenemos CoinGecko.
    *   Fiat/Stocks: Mock/Manual para POC (o API pública sin auth).
*   **Analytics**: Calculadora de Net Worth en tiempo real.

### **3. Frontend (Visualization)**
*   **Components**:
    *   `NetWorthCard`: Total unificado (USD/BTC).
    *   `AssetAllocationChart`: Pie chart (Crypto vs Fiat vs Real Estate).
    *   `HistoryTable`: Lista unificada de movimientos.
*   **Library**: `recharts` (Standard, ligera, D3 based).

---

## 🚀 Plan de Implementación

1.  **Backend**:
    *   Crear `backend/poc/finance_service.py`.
    *   Endpoints: `GET /finance/summary`, `POST /finance/asset`.
2.  **Frontend**:
    *   Instalar `recharts`.
    *   Crear sección "Financial Dashboard" en `page.tsx`.

## 🛡️ Security Note
A diferencia de Mint o YNAB, **Sentinel NO pide tus claves bancarias**.
Es un modelo "Sovereign Individual": Tú controlas los datos, tú los ingresas (o importas CSVs cifrados).

**¿Procedemos con esta arquitectura de "Sovereign Finance"?**

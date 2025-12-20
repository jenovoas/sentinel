# 🦅 Sentinel Triad Browser - The Unified Vision

**Concepto**: Unificar los tres pilares de privacidad en una sola herramienta. ¿Por qué elegir si podemos tenerlo todo?

## The Three Pillars (Arquitectura Triad)

1.  **👻 Ghost Mode (Nym Mixnet)**
    *   **Función**: Anonimato matemático. Protege metadatos, timing y patrón de tráfico.
    *   **Uso**: Whistleblowing, comunicación ultra-sensible, evitar análisis de tráfico global.
    *   **Implementación**: Enrutamiento a cliente local Nym.

2.  **🕸️ Deep Mode (I2P)**
    *   **Función**: Red descentralizada invisible. No depende de servidores de salida.
    *   **Uso**: Acceso a servicios internos de Sentinel, chats P2P, marketplaces internos.
    *   **Implementación**: Enrutamiento a router I2P local.

3.  **⚡ Velocity Mode (Custom Rotating Proxies)**
    *   **Función**: Salida limpia a la "Clear Web" (bancos, exchanges).
    *   **Uso**: Operaciones diarias que requieren velocidad y parecer un "usuario normal" (pero con IP rotativa y limpia).
    *   **Implementación**: Gestor de túneles SSH/VPN efímeros gestionados por Sentinel.

---

## ⏱️ Estimación de Desarrollo

### **Phase A: The Core (POC) - 2-3 Días**
*   **Backend "Switchboard"**: Un servicio proxy (Python) que puede cambiar dinámicamente el upstream (Nym, I2P, Proxy) según el modo elegido.
*   **Sanitization Layer**: El "lavado" de HTML que ya diseñamos.
*   **UI Integration**: Selector de modo en el frontend.
*   *Nota*: Deberás tener los binarios de Nym/I2P instalados o usaremos mocks para validar el enrutamiento.

### **Phase B: Deep Integration (Alpha) - 2 Semanas**
*   **Embedded Binaries**: Empaquetar clientes Nym/I2P con Sentinel (para no pedirle al usuario que los instale).
*   **Proxy Manager Automated**: Script para desplegar tus propios nodos en AWS/DigitalOcean con un click ("One-click deploy").

### **Phase C: Production & Auditing - 1 Mes**
*   Optimización de latencia (Mixnets son lentas).
*   Audit de seguridad del código de "Switchboard".
*   Fuzzing del sanitizador HTML.

---

## 🛠️ Plan de Acción Inmediato (Hoy)

Vamos a construir el **"Universal Switchboard Proxy"**.

1.  Actualizar `browser_service.py` para soportar **Multi-Upstream Routing**.
2.  Crear la UI con el selector **Triad** (Ghost / Deep / Velocity).
3.  Simular los upstreams (ya que configurar Nym/I2P toma tiempo de setup externo).

**¿Hacemos esto? Es un enfoque único en el mercado.**

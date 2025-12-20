# 🦅 Triad Browser - Data Flow Visualization

Curiosity satisfied? Here is how your data moves through the Sentinel Triad.

```mermaid
graph TD
    User[👤 You / Frontend] -->|HTTPS Request| Switch[🎛️ Universal Switchboard (Backend)]
    
    subgraph "The Triad Router"
        Switch -->|Mode: Clear| Clear[🌐 Direct Internet]
        Switch -->|Mode: Velocity| Velocity[⚡ Rotating Proxy / Tor]
        Switch -->|Mode: Ghost| Ghost[👻 Nym Mixnet]
        Switch -->|Mode: Deep| Deep[🕸️ I2P Network]
    end
    
    Clear -->|Standard Trace| Target[🌍 Target Website]
    Velocity -->|Masked IP| Target
    Ghost -->|Mixing + Delay + Noise| Target
    Deep -->|Eepsite Routing| Hidden[🕵️ Hidden Service]
    
    Target -->|Raw HTML| Switch
    Hidden -->|Raw HTML| Switch
    
    Switch -->|Sanitization (Strip JS/Ads)| SafeHTML[🛡️ Sanitized Content]
    SafeHTML -->|Render| User
```

## 🧠 Why this is different?

1.  **Air Gap Protocol**: Your browser (Frontend) *never* executes code from the target. It only receives inert HTML strings.
2.  **Dynamic Routing**: You change your anonymity strategy per-tab, not per-browser.
3.  **The Mixnet Advantage (Ghost)**: Unlike Tor, Nym adds *fake traffic* (loops) and *timing delays*, making it mathematically impossible to correlate your request entrance with the exit.

---

**Ready for the next level?**
We can add **"Chaining"** later: `Ghost -> Velocity` (Mixnet anonymity + Exit Node speed).

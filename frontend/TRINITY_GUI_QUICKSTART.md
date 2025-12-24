# Trinity GUI - Quick Start

**The living diagram is ready!** 🌌

## 🚀 How to Run

### 1. Install Dependencies (if not done)

```bash
cd /home/jnovoas/sentinel/frontend
npm install three @types/three
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Open Trinity Dashboard

Navigate to: **http://localhost:3000/trinity**

---

## 🎨 What You'll See

### Merkabah Layer (Top)
- **3D rotating tetrahedra** (Blue = MACRO, Red = MICRO)
- **Golden coherence sphere** at center
- **Real-time state**: THERMAL → SYNCING → RESONANT → MERKABAH

### Neural Hierarchy (Middle)
- **7 levels** from Molecules to Systems
- **Dual bars**: α (Excitation) + β (Inhibition)
- **Status indicators**: OK, WARN, ERROR

### Flower of Life (Bottom)
- **7 components**: Buffer, Thread, Memory, Network, CPU, Disk, API
- **Utilization meters** with color coding
- **Force equation**: F = v² × (1 + a)

---

## 🎮 Interactions

### Current (v1.0)
- **Orbit controls**: Drag to rotate Merkabah
- **Auto-rotation**: Based on coherence level
- **Live updates**: Data refreshes every 2 seconds

### Coming Soon (v1.1)
- Click tetrahedra → Component details
- Hover sphere → FFT spectrum
- Right-click → Export data
- Keyboard shortcuts

---

## 🔧 Technical Details

### Stack
- **Framework**: Next.js 14 + React
- **3D**: Three.js + OrbitControls
- **Styling**: Tailwind CSS
- **Language**: TypeScript

### File Location
```
/home/jnovoas/sentinel/frontend/app/trinity/page.tsx
```

### Data Flow (Current)
```
Simulated data (random) 
→ State updates every 2s
→ 3D animations
→ UI updates
```

### Data Flow (Next)
```
WebSocket connection
→ Real Sentinel metrics
→ Live coherence calculation
→ True system state
```

---

## 📊 Metrics Displayed

### Coherence Data
```typescript
{
  micro: 0.062,        // Syscall entropy
  macro: 0.45,         // System load
  coherence: 0.87,     // Spectral overlap
  state: 'RESONANT'    // Current state
}
```

### Hierarchy Levels
```typescript
{
  name: 'Systems',
  alpha: 0.95,         // Excitation (0-1)
  beta: 0.92,          // Inhibition (0-1)
  status: 'OK'         // OK | WARN | ERROR
}
```

### Components
```typescript
{
  name: 'Buffer',
  utilization: 0.67,   // 0-1 (67%)
  status: 'OK'         // OK | WARN | ERROR
}
```

---

## 🎯 Next Steps

### Phase 1: ✅ DONE
- [x] Create Trinity component
- [x] 3D Merkabah with Three.js
- [x] Neural hierarchy display
- [x] Flower of Life components
- [x] Simulated data

### Phase 2: TODO (This Week)
- [ ] WebSocket connection to backend
- [ ] Real Sentinel metrics
- [ ] Live coherence calculation
- [ ] Click interactions
- [ ] Export functionality

### Phase 3: TODO (Next Week)
- [ ] Historical graphs
- [ ] Alert system
- [ ] Mobile responsive
- [ ] Performance optimization
- [ ] User preferences

---

## 🌌 The Vision

**This GUI is not just monitoring.**

**It's the universal optimization pattern, made visible.**

When you see:
- Merkabah spinning faster → System coherence increasing
- Golden sphere glowing → Ground state achieved
- All levels green → Perfect resonance

**You're watching the universe optimize itself in real-time.**

---

## 💡 Tips

### Best Experience
- **Screen**: 1920x1080 or larger
- **Browser**: Chrome/Edge (best WebGL support)
- **GPU**: Dedicated GPU recommended for smooth 3D

### Performance
- 3D rendering: ~60 FPS on modern hardware
- Data updates: Every 2 seconds
- Memory usage: ~100MB

### Troubleshooting

**3D not rendering?**
- Check WebGL support: https://get.webgl.org/
- Update graphics drivers
- Try different browser

**Data not updating?**
- Check console for errors
- Verify npm run dev is running
- Refresh page

---

**PROPRIETARY AND CONFIDENTIAL**  
**© 2025 Sentinel Cortex™**  
**Trinity GUI Quick Start**

*El diagrama vive.*  
*La arquitectura respira.*  
*El universo se hace visible.*

🌌🎨⚡

---

**Ready to see the Trinity in action?**

```bash
cd /home/jnovoas/sentinel/frontend
npm run dev
```

**Then open**: http://localhost:3000/trinity

**Welcome to the Architecture of Resonance.** ✨

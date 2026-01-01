<script lang="ts">
  import { onMount } from "svelte";
  import { invoke } from "@tauri-apps/api/tauri";

  // Sentinel State (Legacy Svelte 4 Reactivity)
  let entropy = 0.12;
  let coherence = 0.99;
  let tte = 3.23;
  let sessions = 4;
  let userInput = "";
  let messages = [
    { type: "system", text: "> Uplink established..." },
    { type: "ai", text: "[IA] Sentinel v0.4 online. Waiting for intent." },
  ];

  // Animation Loop (Real-Time Resonance)
  onMount(() => {
    const interval = setInterval(async () => {
      try {
        // @ts-ignore
        if (typeof window !== "undefined" && window.__TAURI_IPC__) {
          // Read "The Truth" from Rust Backend (SHM)
          const state = (await invoke("get_system_vector")) as any;
          entropy = state.entropy;
          coherence = state.coherence;
          tte = state.tte_us;
        } else {
          // Browser Fallback (Mock for UI testing)
          entropy = 0.1 + Math.random() * 0.05;
          if (Math.random() > 0.9) tte = 3.2 + Math.random() * 0.1;
        }
      } catch (e) {
        console.error("Link Error:", e);
      }
    }, 50); // High frequency update (20Hz)
    return () => clearInterval(interval);
  });

  async function handleInput(e: KeyboardEvent) {
    if (e.key === "Enter" && userInput.trim()) {
      const cmd = userInput;
      messages = [...messages, { type: "user", text: `> ${cmd}` }];
      userInput = "";

      // Call Rust Backend (The Bridge)
      try {
        messages = [
          ...messages,
          { type: "system", text: "[IA] Processing vector..." },
        ];

        let response;
        // @ts-ignore
        if (typeof window !== "undefined" && window.__TAURI_IPC__) {
          response = (await invoke("execute_semantic_command", {
            prompt: cmd,
          })) as string;
        } else {
          // Browser Mock Response
          await new Promise((r) => setTimeout(r, 800));
          response = `[BROWSER_MOCK] Identity confirmed. Intent '${cmd}' logged. (Run in Tauri for Real Execution)`;
        }

        messages = [...messages, { type: "ai", text: response }];
      } catch (err) {
        messages = [...messages, { type: "system", text: `Error: ${err}` }];
      }
    }
  }
</script>

<main>
  <!-- TOP HEADER -->
  <header>
    <div class="logo">[SENTINEL_CORTEX v2.0]</div>
    <div class="tte-indicator">
      TTE: {tte.toFixed(2)}μs <span class="pulse">●</span>
    </div>
  </header>

  <!-- MAIN GRID -->
  <div class="grid-container">
    <!-- LEFT: ENTROPY VISUALIZER -->
    <div class="panel entropy-panel">
      <h3>// KERNEL_RESONANCE</h3>
      <div class="wave-container">
        <!-- SVG Waveform Mock -->
        <svg viewBox="0 0 100 20" preserveAspectRatio="none">
          <path
            d="M0 10 Q 25 {10 + entropy * 50}, 50 10 T 100 10"
            stroke="#FFB800"
            stroke-width="0.5"
            fill="none"
          />
          <path
            d="M0 10 Q 25 {10 - entropy * 30}, 50 10 T 100 10"
            stroke="#00F3FF"
            stroke-width="0.5"
            fill="none"
          />
        </svg>
      </div>
      <div class="metrics">
        <div class="metric">ENTROPY: {entropy.toFixed(4)}</div>
        <div class="metric">COHERENCE: {coherence.toFixed(4)}</div>
      </div>
    </div>

    <!-- RIGHT: NEURAL TERMINAL -->
    <div class="panel chat-panel">
      <h3>// NEURAL_UPLINK</h3>
      <div class="chat-history">
        {#each messages as msg}
          <div class="msg {msg.type}">{msg.text}</div>
        {/each}
      </div>
      <div class="input-area">
        <span class="prompt">🧠 sem></span>
        <input
          type="text"
          placeholder="Express intent..."
          bind:value={userInput}
          on:keydown={handleInput}
        />
      </div>
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    background-color: #050505;
    color: #00f3ff;
    font-family: "JetBrains Mono", "Courier New", monospace;
    overflow: hidden;
  }

  :global(*),
  :global(*::before),
  :global(*::after) {
    box-sizing: border-box;
  }

  main {
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 1rem;
    background: #050505;
    color: #00f3ff;
    border: 1px solid #333;
  }

  header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    border-bottom: 1px solid #333;
    padding-bottom: 0.5rem;
    font-size: 0.9rem;
    letter-spacing: 1px;
  }

  .pulse {
    color: #ff003c;
    animation: blink 1s infinite;
  }

  .grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    flex: 1;
    min-height: 0; /* Fix grid overflow */
  }

  .panel {
    border: 1px solid #1a1a1a;
    background: rgba(255, 255, 255, 0.02);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  h3 {
    margin: 0 0 1rem 0;
    font-size: 0.8rem;
    color: #666;
    border-bottom: 1px dashed #333;
    padding-bottom: 0.5rem;
  }

  /* Entropy Styles */
  .wave-container {
    flex: 1;
    border: 1px solid #333;
    background: #000;
    position: relative;
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: 100%;
  }

  .metrics {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
    font-family: monospace;
    font-size: 1.2rem;
  }

  /* Chat Styles */
  .chat-history {
    flex: 1;
    border: 1px solid #333;
    background: #080808;
    padding: 0.5rem;
    font-family: "Courier New", monospace;
    font-size: 0.9rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }

  .msg {
    margin-bottom: 0.5rem;
    word-wrap: break-word;
  }
  .msg.system {
    color: #666;
  }
  .msg.ai {
    color: #00f3ff;
  }
  .msg.user {
    color: #ffb800;
    text-align: right;
  }

  .input-area {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    border: 1px solid #333;
    padding: 0.5rem;
  }

  .prompt {
    margin-right: 0.5rem;
    color: #ffb800;
  }

  input {
    background: transparent;
    border: none;
    color: #fff;
    flex: 1;
    outline: none;
    font-family: monospace;
    font-size: 1rem;
  }

  @keyframes blink {
    50% {
      opacity: 0;
    }
  }
</style>

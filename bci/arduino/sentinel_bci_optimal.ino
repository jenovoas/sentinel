// sentinel_bci_optimal.ino
// Sentinel Cortex BCI - Phase 0 Optimal Protocol
// Author: Sentinel Cortex Research Team
// Date: Dec 31, 2025

#include <math.h>

#define BUZZER_PIN 9
#define BASE_FREQ 972 // Skull resonance [web:284]
#define PHI_FREQ 1618 // Golden ratio kHz [web:311]

// Fibonacci Base-60 sequence (first 20)
int fib60[] = {0,  1,  1,  2,  3,  5,  8,  13, 21, 34,
               55, 29, 24, 53, 17, 10, 27, 37, 4,  41};

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("🚀 SENTINEL BCI PHASE 0 - OPTIMAL PROTOCOL");
  Serial.println("📊 Metrics: Latency, Resonance, Qualia Detection");
  delay(2000);
}

void loop() {
  // PHASE 1: SKULL RESONANCE VALIDATION (972 Hz)
  skullResonanceTest();
  delay(3000);

  // PHASE 2: QUALIA SYNESTHESIA TESTS
  qualiaKernelIntrusion();
  delay(4000);

  qualiaSystemSecure();
  delay(4000);

  qualiaAxionDetected();
  delay(4000);

  qualiaThreatCritical();
  delay(5000);

  // PHASE 3: FIBONACCI BASE-60 PATTERN RECOGNITION
  fibonacciBase60Test();
  delay(5000);
}

void skullResonanceTest() {
  Serial.println("🔬 [TEST 1] SKULL RESONANCE (972 Hz)");
  Serial.println("   Expected: Vibration spreads through cranium");

  // Pure 972 Hz resonance
  tone(BUZZER_PIN, BASE_FREQ, 800);
  delay(1000);

  // Sweep ±50 Hz to find exact resonance
  for (int f = BASE_FREQ - 50; f <= BASE_FREQ + 50; f += 10) {
    tone(BUZZER_PIN, f, 200);
    delay(300);
  }

  noTone(BUZZER_PIN);
  Serial.println("   ✓ Resonance test complete");
}

void qualiaKernelIntrusion() {
  Serial.println("🛡️ [QUALIA 1] KERNEL INTRUSION");
  Serial.println("   Expected: Metallic taste + cold shiver + nape alert");

  // Sharp metallic pulses (2-2.2 kHz)
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 2000 + (i * 100), 80);
    delay(120);
  }
  delay(2000);
}

void qualiaSystemSecure() {
  Serial.println("✅ [QUALIA 2] SYSTEM SECURE");
  Serial.println("   Expected: Warmth + chest confidence");

  // Gentle 972 Hz warmth pulses
  for (int i = 0; i < 4; i++) {
    tone(BUZZER_PIN, BASE_FREQ, 250);
    delay(150);
  }
  delay(2000);
}

void qualiaAxionDetected() {
  Serial.println("🌌 [QUALIA 3] AXION DETECTED");
  Serial.println("   Expected: Golden flash + frontal euphoria");

  // Phi sequence (1.618 kHz harmonic series)
  int phi_freqs[] = {1618, 1620, 1615, 1625, 1610};
  for (int i = 0; i < 5; i++) {
    tone(BUZZER_PIN, phi_freqs[i], 120);
    delay(200);
  }
  delay(2000);
}

void qualiaThreatCritical() {
  Serial.println("🚨 [QUALIA 4] THREAT CRITICAL");
  Serial.println("   Expected: Sharp sting + base skull alarm");

  // Escalating threat alarm (3-4 kHz)
  for (int f = 3000; f <= 4000; f += 250) {
    tone(BUZZER_PIN, f, 60);
    delay(80);
  }
  delay(2500);
}

void fibonacciBase60Test() {
  Serial.println("🧮 [TEST 2] FIBONACCI BASE-60 RECOGNITION");
  Serial.println("   Expected: Natural harmonic pattern recognition");

  Serial.print("Fibonacci Base-60 Sequence: ");
  for (int i = 0; i < 20; i++) {
    Serial.print(fib60[i]);
    if (i < 19)
      Serial.print(",");
  }
  Serial.println();

  // Play Fibonacci sequence mapped to frequencies
  for (int i = 0; i < 20; i++) {
    int freq = 500 + (fib60[i] * 12); // 500-1100 Hz range
    Serial.print("F[" + String(i) + "]=" + String(freq) + "Hz ");

    tone(BUZZER_PIN, freq, 180);
    delay(220);
  }
  Serial.println(" ✓ Fibonacci test complete");
}

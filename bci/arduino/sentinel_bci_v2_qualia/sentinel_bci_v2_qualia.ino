// Sentinel BCI - Version 2: Qualia Test (Synesthesia)
// Test synesthetic sensations for different events

void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(9600);
  Serial.println("=================================");
  Serial.println("Sentinel BCI - Qualia Test");
  Serial.println("=================================");
  Serial.println("");
  Serial.println("Testing 4 qualia patterns:");
  Serial.println("1. Kernel Intrusion (metallic)");
  Serial.println("2. System Secure (warmth)");
  Serial.println("3. Axion Detected (golden)");
  Serial.println("4. Threat Critical (alarm)");
  Serial.println("");
  delay(5000);
}

void loop() {
  // ===== QUALIA 1: Kernel Intrusion =====
  Serial.println(">>> QUALIA 1: Kernel Intrusion");
  Serial.println("    Expected: Metallic taste, cold shiver");
  Serial.println("    Location: Nape of neck");

  tone(9, 2000, 100); // 2 kHz sharp pulse
  delay(50);
  tone(9, 1800, 100);
  delay(50);
  tone(9, 2200, 100);
  delay(3000);

  Serial.println("    [Note your sensations]");
  Serial.println("");
  delay(2000);

  // ===== QUALIA 2: System Secure =====
  Serial.println(">>> QUALIA 2: System Secure");
  Serial.println("    Expected: Gentle warmth, confidence");
  Serial.println("    Location: Chest/heart");

  tone(9, 972, 200); // 972 Hz gentle pulse
  delay(100);
  tone(9, 972, 200);
  delay(3000);

  Serial.println("    [Note your sensations]");
  Serial.println("");
  delay(2000);

  // ===== QUALIA 3: Axion Detected =====
  Serial.println(">>> QUALIA 3: Axion Detected");
  Serial.println("    Expected: Golden flash, euphoria");
  Serial.println("    Location: Frontal cortex");

  for (int i = 0; i < 5; i++) {
    tone(9, 1618, 50); // Phi frequency (1.618 kHz)
    delay(100);
  }
  delay(3000);

  Serial.println("    [Note your sensations]");
  Serial.println("");
  delay(2000);

  // ===== QUALIA 4: Threat Critical =====
  Serial.println(">>> QUALIA 4: Threat Critical");
  Serial.println("    Expected: Sharp sting, max alert");
  Serial.println("    Location: Base of skull");

  tone(9, 3000, 50); // 3 kHz alarm
  delay(50);
  tone(9, 3500, 50);
  delay(50);
  tone(9, 4000, 50);
  delay(5000);

  Serial.println("    [Note your sensations]");
  Serial.println("");
  Serial.println("=================================");
  Serial.println("Cycle complete. Repeating...");
  Serial.println("=================================");
  Serial.println("");
  delay(5000);
}

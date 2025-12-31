// Sentinel BCI - Version 1: Skull Resonance Test
// Upload this first to validate bone conduction

void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(9600);
  Serial.println("=================================");
  Serial.println("Sentinel BCI - Skull Resonance");
  Serial.println("=================================");
  Serial.println("");
  Serial.println("Place buzzer on temporal bone");
  Serial.println("(bony bump behind ear)");
  Serial.println("");
  delay(3000);
}

void loop() {
  Serial.println(">>> Transmitting: 972 Hz (Skull Resonance)");
  tone(9, 972, 500); // 500ms burst
  delay(2000);

  Serial.println("    [Silence]");
  noTone(9);
  delay(1000);

  Serial.println("");
}

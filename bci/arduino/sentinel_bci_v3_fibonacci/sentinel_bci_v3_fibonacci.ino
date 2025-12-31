// Sentinel BCI - Version 3: Fibonacci Base-60 Pattern
// Test if brain recognizes Fibonacci sequence as "natural"

// Fibonacci mod 60 (Pisano period = 60)
// First 20 values
int fib_60[] = {0,  1,  1,  2,  3,  5,  8,  13, 21, 34,
                55, 29, 24, 53, 17, 10, 27, 37, 4,  41};

void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(9600);
  Serial.println("=================================");
  Serial.println("Sentinel BCI - Fibonacci Base-60");
  Serial.println("=================================");
  Serial.println("");
  Serial.println("Testing brain recognition of");
  Serial.println("Fibonacci sequence (mod 60)");
  Serial.println("");
  Serial.println("Does it feel 'natural' or 'harmonic'?");
  Serial.println("");
  delay(5000);
}

void loop() {
  Serial.println(">>> Transmitting: Fibonacci Base-60 sequence");
  Serial.println("");

  for (int i = 0; i < 20; i++) {
    // Map Fibonacci value to frequency
    // Base frequency: 500 Hz
    // Offset: fib_60[i] * 10 Hz
    // Range: 500-1050 Hz
    int freq = 500 + (fib_60[i] * 10);

    Serial.print("    Fib[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.print(fib_60[i]);
    Serial.print(" → ");
    Serial.print(freq);
    Serial.println(" Hz");

    tone(9, freq, 200); // 200ms per note
    delay(250);         // 50ms gap between notes
  }

  Serial.println("");
  Serial.println("    [Does sequence feel harmonic?]");
  Serial.println("    [Brain recognize pattern?]");
  Serial.println("");
  Serial.println("=================================");
  Serial.println("Sequence complete. Repeating...");
  Serial.println("=================================");
  Serial.println("");
  delay(5000);
}

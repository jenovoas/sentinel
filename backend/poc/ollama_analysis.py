"""
Sentinel Vault POC - Ollama Integration
Password strength analysis con LLM
"""
import httpx
import json
import asyncio
import time


class PasswordAnalyzer:
    """Análisis de passwords con Ollama (phi3:mini)"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = f"{ollama_url}/api/generate"
    
    async def analyze_strength(self, password: str) -> dict:
        """
        Analiza fortaleza de password con Ollama
        
        Args:
            password: Password a analizar
        
        Returns:
            Dict con score, issues, suggestions
        """
        prompt = f"""Analyze this password strength and return ONLY valid JSON:

Password: {password}

Evaluate:
1. Length (minimum 20 characters recommended)
2. Complexity (uppercase, lowercase, numbers, symbols)
3. Common patterns (dictionary words, sequences like 123, abc, pet names, years)
4. Entropy estimation

Return JSON format (no additional text):
{{
  "score": <0-100>,
  "length_ok": <true/false>,
  "has_uppercase": <true/false>,
  "has_lowercase": <true/false>,
  "has_numbers": <true/false>,
  "has_symbols": <true/false>,
  "has_patterns": <true/false>,
  "pattern_type": "<type of pattern if detected>",
  "issues": ["list of issues"],
  "suggestions": ["how to improve"]
}}"""
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": "phi3:mini",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                result = response.json()
                text = result.get("response", "")
                
                # Extraer JSON del response
                start = text.find("{")
                end = text.rfind("}") + 1
                
                if start == -1 or end == 0:
                    raise ValueError("No JSON found in response")
                
                json_str = text[start:end]
                return json.loads(json_str)
        
        except Exception as e:
            print(f"❌ Error analyzing password: {e}")
            # Fallback a análisis básico
            return self._basic_analysis(password)
    
    def _basic_analysis(self, password: str) -> dict:
        """Análisis básico si Ollama falla"""
        score = 0
        issues = []
        suggestions = []
        
        # Length
        if len(password) < 12:
            issues.append("Password too short")
            suggestions.append("Use at least 12 characters")
        else:
            score += 25
        
        # Complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        
        if has_upper: score += 15
        else: issues.append("No uppercase letters")
        
        if has_lower: score += 15
        else: issues.append("No lowercase letters")
        
        if has_digit: score += 15
        else: issues.append("No numbers")
        
        if has_symbol: score += 30
        else: 
            issues.append("No special symbols")
            suggestions.append("Add symbols like !@#$%")
        
        return {
            "score": min(score, 100),
            "length_ok": len(password) >= 12,
            "has_uppercase": has_upper,
            "has_lowercase": has_lower,
            "has_numbers": has_digit,
            "has_symbols": has_symbol,
            "has_patterns": False,
            "pattern_type": "none",
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def benchmark(self, passwords: list, iterations: int = 3) -> dict:
        """Benchmark de análisis con Ollama"""
        times = []
        
        for pwd in passwords:
            pwd_times = []
            for _ in range(iterations):
                start = time.time()
                await self.analyze_strength(pwd)
                elapsed = time.time() - start
                pwd_times.append(elapsed * 1000)
            
            times.append({
                "password_length": len(pwd),
                "average_ms": sum(pwd_times) / len(pwd_times),
                "min_ms": min(pwd_times),
                "max_ms": max(pwd_times)
            })
        
        return {
            "results": times,
            "overall_average_ms": sum(t["average_ms"] for t in times) / len(times)
        }


async def main():
    print("🤖 Sentinel Vault - Ollama Integration POC\n")
    
    analyzer = PasswordAnalyzer()
    
    # Test passwords (débil → fuerte)
    test_passwords = [
        ("password123", "Débil"),
        ("MyDog2024", "Medio (patrón: pet+year)"),
        ("MyP@ssw0rd2024", "Medio-Alto"),
        ("Xk9$mQ2#vL8@pR4&nT6", "Fuerte"),
    ]
    
    print("Test 1: Password Analysis\n")
    for pwd, expected in test_passwords:
        print(f"Password: {pwd} (Expected: {expected})")
        result = await analyzer.analyze_strength(pwd)
        
        print(f"  Score: {result['score']}/100")
        print(f"  Length OK: {result['length_ok']}")
        print(f"  Has patterns: {result['has_patterns']}")
        if result['has_patterns']:
            print(f"  Pattern type: {result.get('pattern_type', 'unknown')}")
        print(f"  Issues: {', '.join(result['issues']) if result['issues'] else 'None'}")
        print(f"  Suggestions: {', '.join(result['suggestions']) if result['suggestions'] else 'None'}")
        print()
    
    # Benchmark
    print("\nTest 2: Performance Benchmark")
    bench_passwords = [pwd for pwd, _ in test_passwords]
    bench_result = await analyzer.benchmark(bench_passwords, iterations=3)
    
    print(f"\n📊 Benchmark Results:")
    for i, result in enumerate(bench_result["results"]):
        print(f"  Password {i+1} (len={result['password_length']}): {result['average_ms']:.2f}ms avg")
    
    print(f"\n  Overall average: {bench_result['overall_average_ms']:.2f}ms")
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())

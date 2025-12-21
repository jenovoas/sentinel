#!/usr/bin/env python3
"""
Benchmark del Algoritmo de Consenso
====================================

Valida accuracy y performance del algoritmo usando claims verificados.

Powered by Google ❤️ | Built with Gemini AI

Métricas:
- Accuracy vs ground truth
- Latencia promedio
- Throughput (claims/segundo)
- False positive/negative rate
"""

import time
import json
from typing import List, Dict
from consensus_algorithm import (
    WeightedConsensusAlgorithm,
    Source,
    SourceType,
    VerificationStatus
)


# Dataset de claims verificados manualmente
# Formato: (claim, ground_truth, sources)
VERIFIED_CLAIMS_DATASET = [
    # VERIFIED - Claims verdaderos con múltiples fuentes
    (
        "La temperatura global ha aumentado 1.1°C desde la era preindustrial",
        True,
        [
            Source("IPCC", SourceType.OFFICIAL, True, 1.0, "2025-01-01"),
            Source("NASA", SourceType.OFFICIAL, True, 1.0, "2025-01-01"),
            Source("Nature Climate", SourceType.ACADEMIC, True, 0.95, "2025-01-01"),
        ]
    ),
    (
        "El PIB de EE.UU. creció 2.1% en Q3 2024",
        True,
        [
            Source("Bureau of Economic Analysis", SourceType.OFFICIAL, True, 1.0, "2024-10-30"),
            Source("Wall Street Journal", SourceType.NEWS_TIER1, True, 0.85, "2024-10-30"),
            Source("Bloomberg", SourceType.NEWS_TIER1, True, 0.85, "2024-10-30"),
        ]
    ),
    (
        "La población mundial superó los 8 mil millones en 2022",
        True,
        [
            Source("UN Population Division", SourceType.OFFICIAL, True, 1.0, "2022-11-15"),
            Source("World Bank", SourceType.OFFICIAL, True, 1.0, "2022-11-15"),
            Source("BBC", SourceType.NEWS_TIER1, True, 0.85, "2022-11-15"),
        ]
    ),
    
    # FABRICATED - Claims falsos desmentidos por fuentes
    (
        "Las vacunas COVID contienen microchips de rastreo",
        False,
        [
            Source("CDC", SourceType.OFFICIAL, False, 1.0, "2021-05-01"),
            Source("WHO", SourceType.OFFICIAL, False, 1.0, "2021-05-01"),
            Source("Johns Hopkins", SourceType.ACADEMIC, False, 0.95, "2021-05-01"),
            Source("Reuters Fact Check", SourceType.NEWS_TIER1, False, 0.85, "2021-05-01"),
        ]
    ),
    (
        "La Tierra es plana según estudios científicos",
        False,
        [
            Source("NASA", SourceType.OFFICIAL, False, 1.0, "2020-01-01"),
            Source("Nature", SourceType.ACADEMIC, False, 0.95, "2020-01-01"),
            Source("National Geographic", SourceType.NEWS_TIER1, False, 0.85, "2020-01-01"),
        ]
    ),
    (
        "El 5G causa cáncer según la OMS",
        False,
        [
            Source("WHO", SourceType.OFFICIAL, False, 1.0, "2023-06-01"),
            Source("FDA", SourceType.OFFICIAL, False, 1.0, "2023-06-01"),
            Source("Lancet Oncology", SourceType.ACADEMIC, False, 0.95, "2023-06-01"),
        ]
    ),
    
    # CONTRADICTED - Claims con fuentes en desacuerdo
    (
        "La inflación alcanzará 5% este año",
        None,  # Contradictorio - no hay ground truth claro
        [
            Source("Economist A", SourceType.EXPERT, True, 0.8, "2025-01-01"),
            Source("Economist B", SourceType.EXPERT, False, 0.8, "2025-01-01"),
            Source("Goldman Sachs", SourceType.EXPERT, True, 0.75, "2025-01-01"),
            Source("JP Morgan", SourceType.EXPERT, False, 0.75, "2025-01-01"),
        ]
    ),
    (
        "La economía entrará en recesión en 2025",
        None,
        [
            Source("IMF", SourceType.OFFICIAL, False, 0.9, "2024-12-01"),
            Source("World Bank", SourceType.OFFICIAL, True, 0.9, "2024-12-01"),
            Source("Financial Times", SourceType.NEWS_TIER1, False, 0.85, "2024-12-01"),
            Source("Wall Street Journal", SourceType.NEWS_TIER1, True, 0.85, "2024-12-01"),
        ]
    ),
    
    # PARTIAL - Claims con evidencia mixta
    (
        "El teletrabajo aumenta la productividad",
        True,  # Mayormente verdadero pero con matices
        [
            Source("Stanford Study", SourceType.ACADEMIC, True, 0.85, "2024-06-01"),
            Source("Harvard Business Review", SourceType.ACADEMIC, True, 0.80, "2024-06-01"),
            Source("McKinsey Report", SourceType.EXPERT, False, 0.75, "2024-06-01"),
        ]
    ),
    (
        "El cambio climático afecta la frecuencia de huracanes",
        True,
        [
            Source("NOAA", SourceType.OFFICIAL, True, 0.95, "2024-09-01"),
            Source("Nature Climate", SourceType.ACADEMIC, True, 0.90, "2024-09-01"),
            Source("Climate Skeptic", SourceType.COMMUNITY, False, 0.50, "2024-09-01"),
        ]
    ),
    
    # UNVERIFIED - Claims sin fuentes suficientes
    (
        "Habrá vida en Marte en 2050",
        None,  # No verificable aún
        []  # Sin fuentes
    ),
]


class ConsensusBenchmark:
    """Benchmark del algoritmo de consenso"""
    
    def __init__(self):
        self.algorithm = WeightedConsensusAlgorithm()
        
    def run_benchmark(self) -> Dict:
        """Ejecuta el benchmark completo"""
        print("="*70)
        print("BENCHMARK - ALGORITMO DE CONSENSO PONDERADO")
        print("="*70)
        print(f"\nDataset: {len(VERIFIED_CLAIMS_DATASET)} claims verificados")
        print("\nEjecutando benchmark...\n")
        
        results = []
        total_time = 0
        
        correct_predictions = 0
        total_predictions = 0
        
        false_positives = 0  # Claim falso marcado como verdadero
        false_negatives = 0  # Claim verdadero marcado como falso
        
        for i, (claim, ground_truth, sources) in enumerate(VERIFIED_CLAIMS_DATASET, 1):
            result = self.algorithm.verify_claim(claim, sources)
            total_time += result.processing_time_ms
            
            # Determinar si la predicción es correcta
            predicted_true = result.status in [
                VerificationStatus.VERIFIED,
                VerificationStatus.PARTIAL
            ]
            
            # Solo evaluar accuracy si hay ground truth
            if ground_truth is not None:
                total_predictions += 1
                
                if predicted_true == ground_truth:
                    correct_predictions += 1
                    status_icon = "✅"
                else:
                    status_icon = "❌"
                    if ground_truth is False and predicted_true is True:
                        false_positives += 1
                    elif ground_truth is True and predicted_true is False:
                        false_negatives += 1
                
                print(f"{status_icon} Claim {i}: {result.status.value} "
                      f"(confidence: {result.confidence*100:.1f}%, "
                      f"time: {result.processing_time_ms:.2f}ms)")
            else:
                print(f"⚪ Claim {i}: {result.status.value} "
                      f"(no ground truth, time: {result.processing_time_ms:.2f}ms)")
            
            results.append({
                'claim': claim[:50] + "..." if len(claim) > 50 else claim,
                'status': result.status.value,
                'confidence': result.confidence,
                'ground_truth': ground_truth,
                'correct': predicted_true == ground_truth if ground_truth is not None else None,
                'processing_time_ms': result.processing_time_ms
            })
        
        # Calcular métricas
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        avg_latency = total_time / len(VERIFIED_CLAIMS_DATASET)
        throughput = 1000 / avg_latency  # claims/segundo
        
        false_positive_rate = (false_positives / total_predictions * 100) if total_predictions > 0 else 0
        false_negative_rate = (false_negatives / total_predictions * 100) if total_predictions > 0 else 0
        
        # Imprimir resultados
        print("\n" + "="*70)
        print("RESULTADOS")
        print("="*70)
        
        print(f"\n📊 Accuracy:")
        print(f"  Predicciones correctas: {correct_predictions}/{total_predictions}")
        print(f"  Accuracy:               {accuracy:.1f}%")
        print(f"  False positives:        {false_positives} ({false_positive_rate:.1f}%)")
        print(f"  False negatives:        {false_negatives} ({false_negative_rate:.1f}%)")
        
        print(f"\n⚡ Performance:")
        print(f"  Latencia promedio:      {avg_latency:.2f}ms")
        print(f"  Latencia total:         {total_time:.2f}ms")
        print(f"  Throughput:             {throughput:.0f} claims/segundo")
        
        print(f"\n✅ Criterios de Éxito:")
        criteria = [
            ("Accuracy > 95%", accuracy > 95, f"{accuracy:.1f}%"),
            ("Latencia < 1ms", avg_latency < 1, f"{avg_latency:.2f}ms"),
            ("False positives < 2%", false_positive_rate < 2, f"{false_positive_rate:.1f}%"),
            ("False negatives < 2%", false_negative_rate < 2, f"{false_negative_rate:.1f}%"),
        ]
        
        for criterion, passed, value in criteria:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} - {criterion}: {value}")
        
        # Guardar resultados
        benchmark_results = {
            'accuracy': accuracy,
            'avg_latency_ms': avg_latency,
            'throughput': throughput,
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
            'total_claims': len(VERIFIED_CLAIMS_DATASET),
            'results': results
        }
        
        with open('consensus_benchmark_results.json', 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: consensus_benchmark_results.json")
        
        return benchmark_results


if __name__ == '__main__':
    benchmark = ConsensusBenchmark()
    results = benchmark.run_benchmark()
    
    print("\n" + "="*70)
    print("BENCHMARK COMPLETADO")
    print("="*70)
    print(f"\n✅ Accuracy: {results['accuracy']:.1f}%")
    print(f"✅ Latencia: {results['avg_latency_ms']:.2f}ms")
    print(f"✅ Throughput: {results['throughput']:.0f} claims/segundo")

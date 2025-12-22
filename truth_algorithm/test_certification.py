#!/usr/bin/env python3
"""
Truth Algorithm - Test Suite
=============================

Tests completos para el sistema de certificación de contenido.

Powered by Google ❤️ & Perplexity 💜
"""

import unittest
from source_search import SearchResult, SearchProvider
from consensus_engine import ConsensusEngine, ConsensusResult
from truth_score_calculator import TruthScoreCalculator
from certification_generator import CertificationGenerator


class TestConsensusEngine(unittest.TestCase):
    """Tests para ConsensusEngine"""
    
    def setUp(self):
        self.engine = ConsensusEngine()
    
    def test_consensus_with_official_sources(self):
        """Test con fuentes oficiales (alta confianza)"""
        sources = [
            SearchResult("Title", "https://gov.example", "Snippet", "official", 0.95, "2025-12-21"),
            SearchResult("Title", "https://edu.example", "Snippet", "academic", 0.90, "2025-12-21"),
        ]
        
        result = self.engine.calculate_consensus("Test claim", sources)
        
        self.assertGreater(result.consensus_score, 0.9)
        self.assertEqual(result.confidence_level, "high")
        self.assertEqual(result.num_sources, 2)
    
    def test_consensus_with_mixed_sources(self):
        """Test con fuentes mixtas"""
        sources = [
            SearchResult("Title", "https://news.example", "Snippet", "news", 0.75, "2025-12-21"),
            SearchResult("Title", "https://example.com", "Snippet", "general", 0.60, "2025-12-21"),
        ]
        
        result = self.engine.calculate_consensus("Test claim", sources)
        
        self.assertGreater(result.consensus_score, 0.6)
        self.assertLess(result.consensus_score, 0.8)
    
    def test_consensus_with_no_sources(self):
        """Test sin fuentes"""
        result = self.engine.calculate_consensus("Test claim", [])
        
        self.assertEqual(result.consensus_score, 0.0)
        self.assertEqual(result.confidence_level, "none")
        self.assertEqual(result.num_sources, 0)
    
    def test_consensus_with_single_source(self):
        """Test con una sola fuente (baja confianza)"""
        sources = [
            SearchResult("Title", "https://example.com", "Snippet", "general", 0.70, "2025-12-21"),
        ]
        
        result = self.engine.calculate_consensus("Test claim", sources)
        
        # Con una sola fuente, confianza debe ser baja
        self.assertEqual(result.confidence_level, "low")


class TestTruthScoreCalculator(unittest.TestCase):
    """Tests para TruthScoreCalculator"""
    
    def setUp(self):
        self.calculator = TruthScoreCalculator()
    
    def test_all_claims_verified(self):
        """Test con todos los claims verificados"""
        results = [
            ConsensusResult("Claim 1", 0.95, 3, {"official": 1, "academic": 2}, "high"),
            ConsensusResult("Claim 2", 0.90, 3, {"academic": 2, "news": 1}, "high"),
            ConsensusResult("Claim 3", 0.85, 2, {"news": 2}, "medium"),
        ]
        
        score = self.calculator.calculate(results)
        
        self.assertGreater(score.overall_score, 0.85)
        self.assertEqual(score.claims_verified, 3)
        self.assertEqual(score.claims_total, 3)
        self.assertEqual(score.verification_rate, 1.0)
    
    def test_partial_verification(self):
        """Test con verificación parcial"""
        results = [
            ConsensusResult("Claim 1", 0.80, 3, {"official": 1}, "high"),
            ConsensusResult("Claim 2", 0.40, 1, {"general": 1}, "low"),  # No verificado
        ]
        
        score = self.calculator.calculate(results)
        
        self.assertEqual(score.claims_verified, 1)
        self.assertEqual(score.claims_total, 2)
        self.assertEqual(score.verification_rate, 0.5)
        # Debe haber penalización
        self.assertLess(score.overall_score, 0.6)
    
    def test_no_claims(self):
        """Test sin claims"""
        score = self.calculator.calculate([])
        
        self.assertEqual(score.overall_score, 0.0)
        self.assertEqual(score.claims_total, 0)


class TestCertificationGenerator(unittest.TestCase):
    """Tests para CertificationGenerator"""
    
    def setUp(self):
        self.generator = CertificationGenerator(provider=SearchProvider.MOCK)
    
    def test_certify_simple_content(self):
        """Test certificación de contenido simple"""
        content = "Python es un lenguaje de programación. Fue creado en 1991."
        
        certificate = self.generator.certify(content)
        
        self.assertIsNotNone(certificate.certificate_id)
        self.assertIsNotNone(certificate.content_hash)
        self.assertGreater(certificate.truth_score, 0.0)
        self.assertGreater(certificate.claims_total, 0)
        self.assertEqual(certificate.provider, "mock")
    
    def test_certify_with_explicit_claims(self):
        """Test con claims explícitos"""
        content = "Test content"
        claims = [
            "Python fue creado por Guido van Rossum",
            "Python fue lanzado en 1991"
        ]
        
        certificate = self.generator.certify(content, claims=claims)
        
        self.assertEqual(certificate.claims_total, 2)
        self.assertGreater(certificate.sources_total, 0)
    
    def test_certificate_json_export(self):
        """Test exportación a JSON"""
        content = "Python es un lenguaje de programación."
        certificate = self.generator.certify(content)
        
        json_str = certificate.to_json()
        
        self.assertIn("truth_score", json_str)
        self.assertIn("certificate_id", json_str)
        self.assertIn("verdict", json_str)


class TestIntegration(unittest.TestCase):
    """Tests de integración end-to-end"""
    
    def test_full_certification_pipeline(self):
        """Test del pipeline completo de certificación"""
        # Contenido con múltiples claims
        content = """
        Python es un lenguaje de programación de alto nivel.
        Fue creado por Guido van Rossum y lanzado en 1991.
        Es ampliamente usado en ciencia de datos y desarrollo web.
        """
        
        generator = CertificationGenerator(provider=SearchProvider.MOCK)
        certificate = generator.certify(content)
        
        # Verificar estructura del certificado
        self.assertIsNotNone(certificate.certificate_id)
        self.assertIsNotNone(certificate.content_hash)
        self.assertIsNotNone(certificate.timestamp)
        
        # Verificar scores
        self.assertGreaterEqual(certificate.truth_score, 0.0)
        self.assertLessEqual(certificate.truth_score, 1.0)
        
        # Verificar estadísticas
        self.assertGreater(certificate.claims_total, 0)
        self.assertGreaterEqual(certificate.claims_verified, 0)
        self.assertGreaterEqual(certificate.verification_rate, 0.0)
        self.assertLessEqual(certificate.verification_rate, 1.0)
        
        # Verificar metadata
        self.assertIn(certificate.confidence_level, ['none', 'low', 'medium', 'high'])
        self.assertIsNotNone(certificate.verdict)
        self.assertEqual(certificate.provider, 'mock')
        
        # Verificar detalles
        self.assertEqual(len(certificate.claim_details), certificate.claims_total)


def run_tests():
    """Ejecutar todos los tests"""
    print("="*70)
    print("TRUTH ALGORITHM - TEST SUITE")
    print("="*70)
    print()
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestConsensusEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestTruthScoreCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestCertificationGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print()
    print("="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"✅ Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Fallidos: {len(result.failures)}")
    print(f"⚠️  Errores: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("🎉 TODOS LOS TESTS PASARON")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Synthetic Claims Dataset Generator for TruthSync Testing
Generates realistic but completely fictional claims for stress testing
"""

import random
import json
import hashlib
from typing import List, Dict
from datetime import datetime, timedelta


class SyntheticClaimsGenerator:
    """Generates realistic synthetic claims for testing"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        
        # Factual claim templates
        self.factual_templates = [
            "{entity} announced {event} on {date}",
            "The {metric} is {value} according to {source}",
            "{location} reported {statistic} in {timeframe}",
            "{organization} confirmed {fact} yesterday",
            "Research shows {finding} in {field}",
            "Data indicates {trend} increased by {percentage}%",
            "{company} stock rose {percentage}% today",
            "Temperature in {city} reached {value}°C",
            "{country} GDP grew {percentage}% last quarter",
            "Scientists discovered {discovery} in {year}",
        ]
        
        # Opinion claim templates
        self.opinion_templates = [
            "I think {subject} is {adjective}",
            "Many believe {statement} will happen",
            "{person} feels that {opinion}",
            "It seems like {observation}",
            "Probably {speculation} next year",
            "Maybe {possibility} in the future",
        ]
        
        # Vocabulary
        self.entities = [
            "Tesla", "Apple", "Microsoft", "Google", "Amazon",
            "The Federal Reserve", "NASA", "WHO", "UN", "EU"
        ]
        
        self.events = [
            "a new product launch", "quarterly earnings",
            "a strategic partnership", "expansion plans",
            "policy changes", "research findings"
        ]
        
        self.metrics = [
            "unemployment rate", "inflation rate", "GDP growth",
            "stock price", "revenue", "market share"
        ]
        
        self.values = [
            "3.5%", "$1.2B", "45%", "2.1 million",
            "87 points", "15.3%", "$250", "1,450"
        ]
        
        self.sources = [
            "Bureau of Labor Statistics", "Federal Reserve",
            "World Bank", "IMF", "Reuters", "Bloomberg"
        ]
        
        self.locations = [
            "California", "New York", "Texas", "London",
            "Tokyo", "Singapore", "Germany", "France"
        ]
        
        self.statistics = [
            "record sales", "new cases", "employment growth",
            "market activity", "trade volume", "production output"
        ]
        
        self.companies = [
            "TechCorp", "GlobalInc", "InnovateCo", "FutureSystems",
            "DataDynamics", "CloudVentures", "SmartSolutions"
        ]
        
        self.cities = [
            "New York", "Los Angeles", "Chicago", "Houston",
            "Phoenix", "Philadelphia", "San Antonio", "San Diego"
        ]
        
        self.countries = [
            "United States", "China", "Japan", "Germany",
            "United Kingdom", "France", "India", "Brazil"
        ]
    
    def generate_factual_claim(self) -> str:
        """Generate a factual claim"""
        template = random.choice(self.factual_templates)
        
        claim = template.format(
            entity=random.choice(self.entities),
            event=random.choice(self.events),
            date=self._random_date(),
            metric=random.choice(self.metrics),
            value=random.choice(self.values),
            source=random.choice(self.sources),
            location=random.choice(self.locations),
            statistic=random.choice(self.statistics),
            timeframe=self._random_timeframe(),
            organization=random.choice(self.entities),
            fact=random.choice(self.events),
            finding=random.choice(self.statistics),
            field="economics",
            trend=random.choice(self.metrics),
            percentage=random.randint(1, 50),
            company=random.choice(self.companies),
            city=random.choice(self.cities),
            country=random.choice(self.countries),
            discovery="new findings",
            year=random.randint(2020, 2024)
        )
        
        return claim
    
    def generate_opinion_claim(self) -> str:
        """Generate an opinion claim"""
        template = random.choice(self.opinion_templates)
        
        claim = template.format(
            subject="the market",
            adjective="volatile",
            statement="changes",
            person="Analysts",
            opinion="growth will continue",
            observation="trends are shifting",
            speculation="rates will rise",
            possibility="expansion"
        )
        
        return claim
    
    def _random_date(self) -> str:
        """Generate random date"""
        days_ago = random.randint(1, 365)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%B %d, %Y")
    
    def _random_timeframe(self) -> str:
        """Generate random timeframe"""
        return random.choice([
            "Q1 2024", "Q2 2024", "last quarter",
            "this year", "2023", "last month"
        ])
    
    def generate_dataset(
        self,
        total_claims: int = 10000,
        factual_ratio: float = 0.7
    ) -> List[Dict]:
        """
        Generate complete dataset
        
        Args:
            total_claims: Total number of claims to generate
            factual_ratio: Ratio of factual vs opinion claims
        """
        dataset = []
        
        factual_count = int(total_claims * factual_ratio)
        opinion_count = total_claims - factual_count
        
        # Generate factual claims
        for i in range(factual_count):
            claim_text = self.generate_factual_claim()
            dataset.append({
                'id': i,
                'text': claim_text,
                'type': 'factual',
                'length': len(claim_text),
                'hash': hashlib.md5(claim_text.encode()).hexdigest(),
                'expected_verifiable': True
            })
        
        # Generate opinion claims
        for i in range(opinion_count):
            claim_text = self.generate_opinion_claim()
            dataset.append({
                'id': factual_count + i,
                'text': claim_text,
                'type': 'opinion',
                'length': len(claim_text),
                'hash': hashlib.md5(claim_text.encode()).hexdigest(),
                'expected_verifiable': False
            })
        
        # Shuffle to mix factual and opinion
        random.shuffle(dataset)
        
        return dataset
    
    def generate_with_distribution(
        self,
        total_claims: int = 10000,
        hot_ratio: float = 0.2,
        cache_hit_target: float = 0.8
    ) -> Dict:
        """
        Generate dataset with realistic cache distribution (Zipf-like)
        
        Args:
            total_claims: Total unique claims
            hot_ratio: Ratio of "hot" claims (frequently accessed)
            cache_hit_target: Target cache hit rate
        
        Returns:
            Dict with 'claims' and 'access_pattern'
        """
        # Generate unique claims
        unique_claims = self.generate_dataset(total_claims)
        
        # Determine hot vs cold claims
        hot_count = int(total_claims * hot_ratio)
        hot_claims = unique_claims[:hot_count]
        cold_claims = unique_claims[hot_count:]
        
        # Generate access pattern (simulates real requests)
        access_pattern = []
        num_requests = 100000  # Simulate 100k requests
        
        for _ in range(num_requests):
            if random.random() < cache_hit_target:
                # Access hot claim (cache hit)
                claim = random.choice(hot_claims)
            else:
                # Access cold claim (cache miss)
                claim = random.choice(cold_claims)
            
            access_pattern.append(claim['id'])
        
        return {
            'claims': unique_claims,
            'access_pattern': access_pattern,
            'stats': {
                'total_unique_claims': total_claims,
                'hot_claims': hot_count,
                'cold_claims': len(cold_claims),
                'total_requests': num_requests,
                'expected_cache_hit_rate': cache_hit_target
            }
        }


def save_dataset(dataset: Dict, filename: str):
    """Save dataset to JSON file"""
    with open(filename, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Dataset saved to {filename}")
    print(f"   Total claims: {len(dataset['claims']):,}")
    print(f"   Total requests: {dataset['stats']['total_requests']:,}")
    print(f"   Expected cache hit rate: {dataset['stats']['expected_cache_hit_rate']*100:.1f}%")


if __name__ == '__main__':
    print("="*70)
    print("TRUTHSYNC SYNTHETIC DATASET GENERATOR")
    print("="*70)
    
    generator = SyntheticClaimsGenerator(seed=42)
    
    # Generate small dataset for quick testing
    print("\n📊 Generating small dataset (1,000 claims)...")
    small_dataset = generator.generate_with_distribution(
        total_claims=1000,
        hot_ratio=0.2,
        cache_hit_target=0.8
    )
    save_dataset(small_dataset, 'synthetic_claims_1k.json')
    
    # Generate medium dataset for stress testing
    print("\n📊 Generating medium dataset (10,000 claims)...")
    medium_dataset = generator.generate_with_distribution(
        total_claims=10000,
        hot_ratio=0.2,
        cache_hit_target=0.8
    )
    save_dataset(medium_dataset, 'synthetic_claims_10k.json')
    
    # Generate large dataset for production simulation
    print("\n📊 Generating large dataset (100,000 claims)...")
    large_dataset = generator.generate_with_distribution(
        total_claims=100000,
        hot_ratio=0.2,
        cache_hit_target=0.8
    )
    save_dataset(large_dataset, 'synthetic_claims_100k.json')
    
    # Show sample claims
    print("\n" + "="*70)
    print("SAMPLE CLAIMS")
    print("="*70)
    
    print("\n🔵 Factual Claims (Verifiable):")
    for claim in small_dataset['claims'][:3]:
        if claim['type'] == 'factual':
            print(f"  - {claim['text']}")
    
    print("\n🟡 Opinion Claims (Not Verifiable):")
    for claim in small_dataset['claims'][:10]:
        if claim['type'] == 'opinion':
            print(f"  - {claim['text']}")
            break
    
    print("\n✅ Datasets generated successfully!")
    print("   Use these for stress testing without exposing real data.")

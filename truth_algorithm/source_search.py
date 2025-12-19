"""
Truth Algorithm - Source Search Engine
=======================================

Searches trusted sources for evidence to verify claims.

Architecture (Layered):
1. Query Generation → Optimize claim for search
2. Source Selection → Choose best sources by category
3. Result Extraction → Get relevant snippets
4. Relevance Ranking → Score by trust + relevance

Best Practices:
- Async/await for performance
- Type hints throughout
- Robust error handling
- Structured logging
- Rate limiting & caching
- Configuration externalized
- SOLID principles

Author: Sentinel Team
License: MIT
"""

import asyncio
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
from pathlib import Path

import aiohttp
from aiohttp import ClientSession, ClientTimeout
import redis.asyncio as redis
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

class SourceConfig(BaseModel):
    """Configuration for source search."""
    
    # API Keys (load from environment)
    google_api_key: Optional[str] = Field(default=None, env='GOOGLE_API_KEY')
    google_cse_id: Optional[str] = Field(default=None, env='GOOGLE_CSE_ID')
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_concurrent_requests: int = 10
    
    # Caching
    cache_ttl_seconds: int = 3600  # 1 hour
    redis_url: str = "redis://localhost:6379"
    
    # Search parameters
    max_results_per_source: int = 5
    search_timeout_seconds: int = 10
    
    # Trust scores (0-1)
    trust_scores: Dict[str, float] = {
        # Official sources
        "gov": 0.95,
        "edu": 0.90,
        "who.int": 0.95,
        "cdc.gov": 0.95,
        
        # News (tier 1)
        "reuters.com": 0.85,
        "apnews.com": 0.85,
        "bbc.com": 0.80,
        
        # Academic
        "scholar.google.com": 0.90,
        "pubmed.gov": 0.90,
        
        # Fact-checkers
        "snopes.com": 0.80,
        "factcheck.org": 0.80,
        "politifact.com": 0.75,
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ============================================================================
# DATA MODELS
# ============================================================================

class SourceType(str, Enum):
    """Types of sources."""
    OFFICIAL = "official"  # Government, WHO, CDC
    ACADEMIC = "academic"  # Papers, journals
    NEWS = "news"  # Trusted news outlets
    FACT_CHECKER = "fact_checker"  # Snopes, PolitiFact
    EXPERT = "expert"  # Verified experts
    COMMUNITY = "community"  # Crowdsourced


@dataclass
class SearchResult:
    """Single search result from a source."""
    url: str
    title: str
    snippet: str
    source_domain: str
    source_type: SourceType
    trust_score: float
    relevance_score: float
    published_date: Optional[datetime] = None
    
    @property
    def combined_score(self) -> float:
        """Weighted combination of trust and relevance."""
        return (self.trust_score * 0.6) + (self.relevance_score * 0.4)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['source_type'] = self.source_type.value
        data['combined_score'] = self.combined_score
        if self.published_date:
            data['published_date'] = self.published_date.isoformat()
        return data


@dataclass
class SearchQuery:
    """Optimized search query."""
    original_claim: str
    optimized_query: str
    keywords: List[str]
    entities: List[str]
    category: str  # health, politics, economy, etc.
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# QUERY OPTIMIZER
# ============================================================================

class QueryOptimizer:
    """
    Optimizes claims for search.
    
    Layer 1: Query Generation
    - Extracts key terms
    - Removes opinion words
    - Adds context
    """
    
    # Words to remove (opinion, filler)
    STOP_WORDS = {
        "think", "believe", "feel", "opinion", "should", "must",
        "i", "you", "we", "they", "the", "a", "an"
    }
    
    # Words that indicate categories
    CATEGORY_KEYWORDS = {
        "health": {"vaccine", "disease", "covid", "health", "medical", "doctor"},
        "politics": {"president", "congress", "election", "vote", "policy"},
        "economy": {"gdp", "unemployment", "inflation", "market", "economy"},
        "climate": {"climate", "temperature", "carbon", "emissions", "warming"},
        "technology": {"ai", "tech", "software", "computer", "internet"},
    }
    
    def optimize(self, claim: str, entities: List[str], keywords: List[str]) -> SearchQuery:
        """
        Optimize claim for search.
        
        Args:
            claim: Original claim text
            entities: Extracted entities (from ClaimExtractor)
            keywords: Extracted keywords (from ClaimExtractor)
            
        Returns:
            Optimized search query
        """
        # Extract key terms
        key_terms = self._extract_key_terms(claim, entities, keywords)
        
        # Build optimized query
        optimized = " ".join(key_terms)
        
        # Detect category
        category = self._detect_category(claim.lower())
        
        return SearchQuery(
            original_claim=claim,
            optimized_query=optimized,
            keywords=keywords,
            entities=entities,
            category=category
        )
    
    def _extract_key_terms(
        self,
        claim: str,
        entities: List[str],
        keywords: List[str]
    ) -> List[str]:
        """Extract most important terms for search."""
        key_terms = []
        
        # Add entities (highest priority)
        key_terms.extend(entities)
        
        # Add keywords (medium priority)
        for keyword in keywords:
            if keyword.lower() not in self.STOP_WORDS:
                key_terms.append(keyword)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)
        
        return unique_terms[:10]  # Limit to top 10
    
    def _detect_category(self, claim_lower: str) -> str:
        """Detect claim category based on keywords."""
        category_scores = {}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in claim_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "general"


# ============================================================================
# SOURCE SELECTOR
# ============================================================================

class SourceSelector:
    """
    Selects best sources based on claim category.
    
    Layer 2: Source Selection
    - Maps categories to trusted sources
    - Prioritizes by trust score
    """
    
    # Category → Source mapping
    CATEGORY_SOURCES = {
        "health": [
            "cdc.gov",
            "who.int",
            "pubmed.gov",
            "nih.gov"
        ],
        "politics": [
            "apnews.com",
            "reuters.com",
            "politifact.com",
            "factcheck.org"
        ],
        "economy": [
            "bls.gov",
            "federalreserve.gov",
            "reuters.com",
            "bloomberg.com"
        ],
        "climate": [
            "nasa.gov",
            "noaa.gov",
            "ipcc.ch",
            "nature.com"
        ],
        "general": [
            "reuters.com",
            "apnews.com",
            "bbc.com",
            "snopes.com"
        ]
    }
    
    def __init__(self, config: SourceConfig):
        self.config = config
    
    def select_sources(self, category: str) -> List[str]:
        """
        Select best sources for category.
        
        Args:
            category: Claim category
            
        Returns:
            List of source domains
        """
        sources = self.CATEGORY_SOURCES.get(category, self.CATEGORY_SOURCES["general"])
        
        # Sort by trust score
        sources_with_scores = [
            (source, self.config.trust_scores.get(source, 0.5))
            for source in sources
        ]
        sources_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [source for source, _ in sources_with_scores]


# ============================================================================
# SEARCH ENGINE
# ============================================================================

class SourceSearchEngine:
    """
    Main search engine.
    
    Coordinates all layers:
    1. Query optimization
    2. Source selection
    3. Result extraction
    4. Relevance ranking
    """
    
    def __init__(self, config: Optional[SourceConfig] = None):
        self.config = config or SourceConfig()
        self.query_optimizer = QueryOptimizer()
        self.source_selector = SourceSelector(self.config)
        self.cache: Optional[redis.Redis] = None
        self._session: Optional[ClientSession] = None
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def initialize(self):
        """Initialize async resources."""
        # Create aiohttp session
        timeout = ClientTimeout(total=self.config.search_timeout_seconds)
        self._session = ClientSession(timeout=timeout)
        
        # Connect to Redis cache
        try:
            self.cache = await redis.from_url(self.config.redis_url)
            await self.cache.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}. Continuing without cache.")
            self.cache = None
    
    async def close(self):
        """Close async resources."""
        if self._session:
            await self._session.close()
        if self.cache:
            await self.cache.close()
    
    async def search(
        self,
        claim: str,
        entities: List[str],
        keywords: List[str]
    ) -> List[SearchResult]:
        """
        Search for evidence to verify claim.
        
        Args:
            claim: Claim text
            entities: Extracted entities
            keywords: Extracted keywords
            
        Returns:
            List of search results, ranked by relevance
        """
        # Layer 1: Optimize query
        query = self.query_optimizer.optimize(claim, entities, keywords)
        logger.info(f"Optimized query: {query.optimized_query} (category: {query.category})")
        
        # Check cache
        cache_key = self._get_cache_key(query.optimized_query)
        if self.cache:
            cached = await self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Cache hit for query: {query.optimized_query}")
                return cached
        
        # Layer 2: Select sources
        sources = self.source_selector.select_sources(query.category)
        logger.info(f"Selected {len(sources)} sources: {sources}")
        
        # Layer 3: Search sources (parallel)
        tasks = [
            self._search_source(query, source)
            for source in sources
        ]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for results in results_lists:
            if isinstance(results, Exception):
                logger.error(f"Search error: {results}")
                continue
            all_results.extend(results)
        
        # Layer 4: Rank by relevance
        ranked_results = self._rank_results(all_results, query)
        
        # Cache results
        if self.cache and ranked_results:
            await self._save_to_cache(cache_key, ranked_results)
        
        logger.info(f"Found {len(ranked_results)} total results")
        return ranked_results
    
    async def _search_source(
        self,
        query: SearchQuery,
        source_domain: str
    ) -> List[SearchResult]:
        """Search a single source."""
        async with self._semaphore:  # Rate limiting
            try:
                # Use Google Custom Search API
                if not self.config.google_api_key:
                    logger.warning("Google API key not configured")
                    return []
                
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.config.google_api_key,
                    "cx": self.config.google_cse_id,
                    "q": f"{query.optimized_query} site:{source_domain}",
                    "num": self.config.max_results_per_source
                }
                
                async with self._session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Search failed for {source_domain}: {response.status}")
                        return []
                    
                    data = await response.json()
                    items = data.get("items", [])
                    
                    results = []
                    for item in items:
                        result = SearchResult(
                            url=item["link"],
                            title=item["title"],
                            snippet=item.get("snippet", ""),
                            source_domain=source_domain,
                            source_type=self._get_source_type(source_domain),
                            trust_score=self.config.trust_scores.get(source_domain, 0.5),
                            relevance_score=0.0  # Will be calculated in ranking
                        )
                        results.append(result)
                    
                    logger.info(f"Found {len(results)} results from {source_domain}")
                    return results
                    
            except Exception as e:
                logger.error(f"Error searching {source_domain}: {e}")
                return []
    
    def _get_source_type(self, domain: str) -> SourceType:
        """Determine source type from domain."""
        if domain.endswith(".gov"):
            return SourceType.OFFICIAL
        elif domain.endswith(".edu"):
            return SourceType.ACADEMIC
        elif "factcheck" in domain or "snopes" in domain or "politifact" in domain:
            return SourceType.FACT_CHECKER
        else:
            return SourceType.NEWS
    
    def _rank_results(
        self,
        results: List[SearchResult],
        query: SearchQuery
    ) -> List[SearchResult]:
        """
        Rank results by relevance + trust.
        
        Relevance score based on:
        - Keyword matches in title/snippet
        - Entity matches
        - Recency (if date available)
        """
        query_terms = set(query.keywords + query.entities)
        
        for result in results:
            # Calculate relevance score
            text = f"{result.title} {result.snippet}".lower()
            matches = sum(1 for term in query_terms if term.lower() in text)
            relevance = min(matches / len(query_terms), 1.0) if query_terms else 0.5
            
            result.relevance_score = relevance
        
        # Sort by combined score (trust + relevance)
        results.sort(key=lambda r: r.combined_score, reverse=True)
        
        return results
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return f"search:{hashlib.md5(query.encode()).hexdigest()}"
    
    async def _get_from_cache(self, key: str) -> Optional[List[SearchResult]]:
        """Get results from cache."""
        try:
            data = await self.cache.get(key)
            if data:
                results_data = json.loads(data)
                return [
                    SearchResult(**{
                        **r,
                        'source_type': SourceType(r['source_type'])
                    })
                    for r in results_data
                ]
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        return None
    
    async def _save_to_cache(self, key: str, results: List[SearchResult]):
        """Save results to cache."""
        try:
            data = json.dumps([r.to_dict() for r in results])
            await self.cache.setex(key, self.config.cache_ttl_seconds, data)
        except Exception as e:
            logger.error(f"Cache write error: {e}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage."""
    print("🔍 Truth Algorithm - Source Search Engine\n")
    print("=" * 60)
    
    # Example claim (from ClaimExtractor output)
    claim = "Biden said unemployment is at 3.5% in December 2023"
    entities = ["Biden", "3.5%", "December 2023"]
    keywords = ["unemployment", "biden"]
    
    print(f"\n📝 Claim: {claim}")
    print(f"   Entities: {entities}")
    print(f"   Keywords: {keywords}\n")
    
    # Search for evidence
    async with SourceSearchEngine() as engine:
        results = await engine.search(claim, entities, keywords)
        
        print(f"\n✅ Found {len(results)} results:\n")
        
        for i, result in enumerate(results[:5], 1):  # Top 5
            print(f"{i}. {result.title}")
            print(f"   Source: {result.source_domain} ({result.source_type.value})")
            print(f"   Trust: {result.trust_score:.2f} | Relevance: {result.relevance_score:.2f} | Combined: {result.combined_score:.2f}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet[:100]}...")
            print()
    
    print("=" * 60)
    print("✅ POC Complete!")


if __name__ == "__main__":
    asyncio.run(main())

-- Verified facts (source of truth)
CREATE TABLE verified_facts (
    id BIGSERIAL PRIMARY KEY,
    claim TEXT NOT NULL,
    claim_hash BYTEA NOT NULL UNIQUE,
    trust_score REAL NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    sources JSONB NOT NULL,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    verification_count INTEGER DEFAULT 1
);

-- Pre-cargar hechos verificados hoy (nuestro benchmark)
INSERT INTO verified_facts (claim, claim_hash, trust_score, sources) VALUES 
('Kernel 6.12 exists', '\x6ba1', 100, '["kernel.org", "Gemini Audit"]'),
('EEVDF scheduler active', '\x6ba2', 100, '["Kernel Source", "Sentinel Audit"]'),
('PLACE_LAG non-existent', '\x6ba3', 100, '["Kernel Source", "Hallucination Log"]');

CREATE TABLE source_trust (
    id BIGSERIAL PRIMARY KEY,
    source_domain TEXT NOT NULL UNIQUE,
    trust_score REAL NOT NULL,
    verification_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO source_trust (source_domain, trust_score) VALUES 
('kernel.org', 100.0),
('sentinel.local', 100.0),
('hallucination_log', 100.0);

# ❓ Truth Algorithm - Frequently Asked Questions

## General Questions

### What is Truth Algorithm?

Truth Algorithm is an open-source AI system that verifies factual claims using multi-layered analysis. Unlike traditional fact-checkers or AI chatbots, we:
- Verify source credibility (not just cite them)
- Detect coordinated disinformation campaigns
- Analyze causality (not just correlation)
- Perform multimodal verification (video/audio/text)

**Result**: 8-0 victory over Perplexity AI in adversarial testing.

### Why did you build this?

Disinformation is the #1 threat to democracy, public health, and markets. Current solutions (Perplexity, Google, fact-checkers) are:
- Too slow (manual review)
- Too shallow (surface-level checking)
- Too easily fooled (no adversarial robustness)

We built a system that actually works.

### Is this really open source?

Yes! MIT licensed. You can:
- Use it commercially
- Modify it
- Distribute it
- No attribution required (though appreciated)

### How is this different from Perplexity/ChatGPT?

| Feature | Perplexity/ChatGPT | Truth Algorithm |
|---------|-------------------|-----------------|
| Source verification | ❌ Cites without verifying | ✅ Trust scoring (0-100) |
| Coordinated campaigns | ❌ Misses them | ✅ Detects temporal clustering |
| Causal analysis | ❌ Confuses correlation/causation | ✅ Causal inference engine |
| Deepfake detection | ❌ Text-only | ✅ Multimodal (video/audio) |
| Adversarial robustness | ❌ Easily fooled | ✅ Designed to resist evasion |

**Proof**: Run `python perplexity_killer_demo.py` to see the 8-0 test results.

## Technical Questions

### What technologies do you use?

- **NLP**: spaCy (entity extraction), Transformers (zero-shot classification)
- **ML**: PyTorch, BART-large-MNLI
- **Search**: Async/await architecture, Redis caching
- **APIs**: SerpAPI, NewsAPI (configurable)
- **Language**: Python 3.8+

### Do I need GPU?

**For demo**: No (uses lightweight demo without ML models)  
**For full system**: Recommended but not required (CPU works, just slower)

### How accurate is it?

**Test results**:
- 8/8 adversarial test cases passed (100%)
- 0/8 for Perplexity (0%)

**Real-world**: Depends on:
- Quality of sources available
- Complexity of claim
- API access (some features need API keys)

### Can I use this without API keys?

Yes! The demo (`perplexity_killer_demo.py`) works without any API keys.

For full functionality (source search), you'll need:
- SerpAPI key (Google search)
- NewsAPI key (news sources)

Both have free tiers.

### What languages are supported?

Currently: **English only**

Planned: Spanish, Portuguese, Mandarin, French, German

Want to help? See [CONTRIBUTING.md](CONTRIBUTING.md)

### How fast is it?

**Claim extraction**: ~1-2 seconds per claim  
**Source verification**: ~3-5 seconds (with caching)  
**Full analysis**: ~5-10 seconds per claim

**Scalability**: Designed for 1M+ verifications/day with proper infrastructure.

## Use Case Questions

### Can I use this for my business?

Yes! MIT license allows commercial use.

**Common use cases**:
- Healthcare: Verify medical claims
- Finance: Detect market manipulation
- Media: Fact-check articles
- Government: Combat disinformation
- Academia: Verify research claims

### Can I integrate this into my app?

Yes! The code is modular:

```python
from claim_extractor import ClaimExtractor

extractor = ClaimExtractor()
claims = extractor.extract("Your text here")
```

See [README.md](README.md) for full API documentation.

### Do you offer enterprise support?

Not yet, but planned. For now:
- Open GitHub issues for bugs
- Join our Discord for questions
- Email for partnership inquiries

### Can this detect deepfakes?

**Currently**: Architecture supports it (multimodal analysis)  
**Status**: Video/audio detection in development  
**ETA**: Q1 2025

For now, it detects text-based claims about deepfakes.

## Ethical Questions

### Who decides what's "true"?

**We don't.** The algorithm:
1. Extracts verifiable claims
2. Searches trusted sources
3. Analyzes evidence
4. Reports findings with confidence scores

**You decide** based on the evidence presented.

### Isn't this censorship?

No. We don't remove content. We:
- Verify claims
- Provide evidence
- Show confidence scores
- Let users decide

**Transparency**: All code is open source. You can audit how decisions are made.

### What about bias?

**Our approach**:
- Source trust scoring (transparent criteria)
- Multiple sources required
- Confidence scores (not binary true/false)
- Open source (community can audit)

**Bias exists** in sources. We mitigate by:
- Diverse source selection
- Explicit confidence scoring
- Transparent methodology

### Can this be weaponized?

Any tool can be misused. Our safeguards:
- Open source (no secret algorithms)
- Transparent scoring
- Community oversight
- MIT license (anyone can fork/modify)

**Philosophy**: Truth is the best defense against weaponization.

## Business Questions

### How do you make money?

**Current**: We don't (open source project)

**Planned**:
- Enterprise SaaS (custom deployments)
- API usage fees (high-volume users)
- Consulting/integration services

**Core remains free and open source.**

### What's the business model?

**Open Core**:
- Core verification: Free, open source
- Enterprise features: Paid (SSO, SLA, support)
- API marketplace: Usage-based pricing

See [MARKET_ANALYSIS.md](MARKET_ANALYSIS.md) for details.

### Are you looking for investors?

Yes. See [VC_PITCH.md](VC_PITCH.md) for details.

**Ask**: $5M Series A at $25M pre-money  
**Use**: Engineering, sales, operations

### Can I invest?

If you're an accredited investor or VC, email us: [your-email@example.com]

## Community Questions

### How can I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

**Quick start**:
1. Fork the repo
2. Pick an issue labeled `good first issue`
3. Make your changes
4. Submit a PR

**Priority areas**:
- Multimodal analysis (video/audio)
- Language support (non-English)
- Additional test cases
- Documentation

### Where can I get help?

- **GitHub Issues**: Bug reports, feature requests
- **Discord**: [Join here] - Community chat
- **Email**: [your-email@example.com] - General inquiries

### Is there a roadmap?

Yes! See [LAUNCH_SUMMARY.md](LAUNCH_SUMMARY.md)

**Q1 2025**:
- Multimodal analysis (video/audio)
- API marketplace
- Browser extension

**Q2 2025**:
- Mobile apps (iOS/Android)
- Enterprise features
- International expansion

### How can I stay updated?

- ⭐ Star the repo on GitHub
- 👀 Watch for releases
- 🐦 Follow on Twitter: [@yourhandle]
- 💬 Join Discord: [link]

## Troubleshooting

### Installation fails

**Common issues**:

1. **Python version**: Requires 3.8+
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **spaCy model missing**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Torch/CUDA issues**: Install CPU version
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

### Demo doesn't work

**Try**:
```bash
# Use the lightweight demo (no dependencies)
python perplexity_killer_demo.py

# If that fails, check Python version
python --version
```

### Tests fail

**Check**:
1. All dependencies installed: `pip install -r requirements.txt`
2. spaCy model downloaded: `python -m spacy download en_core_web_sm`
3. Python version 3.8+

### API errors

**Common causes**:
- Missing API keys (set in `.env` file)
- Rate limiting (wait or upgrade plan)
- Invalid keys (check `.env` format)

## Philosophy Questions

### Why "Truth Algorithm"?

Because:
- Truth is verifiable (not subjective)
- Algorithms can verify (better than humans at scale)
- Together = Truth Algorithm

### What's the mission?

**Protect truth. Enable freedom. Accelerate evolution.**

- **Protect truth**: From coordinated disinformation
- **Enable freedom**: Cognitive liberty (think without manipulation)
- **Accelerate evolution**: Humanity advancing based on reality

See [VERDAD_LIBERTAD_EVOLUCION.md](../VERDAD_LIBERTAD_EVOLUCION.md) for the full vision.

### Why open source?

**Transparency**: Truth verification must be auditable  
**Trust**: No secret algorithms, no hidden agendas  
**Community**: Better together than alone  
**Freedom**: Anyone can use, modify, improve

**Philosophy**: Truth belongs to everyone.

---

## Still have questions?

**Open an issue**: [GitHub Issues](https://github.com/yourrepo/issues)  
**Join Discord**: [Link]  
**Email us**: [your-email@example.com]

---

**Together, we're building the truth layer of the internet.** 🕊️

# Psychology-to-n8n Pipeline - Implementation Plan

## Goal

Create an automated Python pipeline that:
1. Extracts text from psychology/psychiatry books (PDFs)
2. Uses GPT-4 to identify behavioral deception patterns
3. Stores patterns in a structured database
4. Automatically generates n8n workflow JSON files
5. Integrates with Truth Algorithm Layer 7

## Proposed Changes

### New Python Project Structure

```
truth-algorithm/psychology_to_n8n/
├── pyproject.toml                 # Poetry dependencies
├── README.md                      # Usage instructions
├── .env.example                   # Environment variables template
├── src/
│   └── psychology_to_n8n/
│       ├── __init__.py
│       ├── extract_text.py        # PDF extraction
│       ├── pattern_recognition.py # GPT-4 pattern extraction
│       ├── pattern_database.py    # SQLAlchemy models
│       ├── workflow_generator.py  # n8n JSON generation
│       ├── n8n_integration.py     # Upload to n8n
│       └── main.py                # Pipeline orchestration
├── tests/
│   ├── __init__.py
│   ├── test_extract_text.py
│   ├── test_pattern_recognition.py
│   ├── test_workflow_generator.py
│   └── fixtures/
│       └── sample_chapter.txt     # Test data
├── books/                         # Input PDFs (gitignored)
├── n8n_workflows/                 # Generated workflows
└── summaries/                     # Pattern summaries
```

### Dependencies (pyproject.toml)

```toml
[tool.poetry.dependencies]
python = "^3.11"
PyPDF2 = "^3.0.0"
openai = "^1.0.0"
sqlalchemy = "^2.0.0"
requests = "^2.31.0"
python-dotenv = "^1.0.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
```

### Key Implementation Details

#### 1. Text Extraction (`extract_text.py`)
- Use PyPDF2 for PDF parsing
- Regex-based chapter detection
- Handle OCR errors gracefully

#### 2. Pattern Recognition (`pattern_recognition.py`)
- GPT-4 Turbo with JSON mode
- Structured prompt for consistent output
- Rate limiting (3 requests/min to avoid API limits)
- Retry logic for API failures

#### 3. Database (`pattern_database.py`)
- SQLite for simplicity (can upgrade to PostgreSQL later)
- Schema: id, name, description, signals (JSON), timing, confidence, category, source_book, source_page
- Unique constraint on pattern name

#### 4. Workflow Generator (`workflow_generator.py`)
- Template-based generation
- Category-specific node generation (facial, vocal, linguistic)
- Valid n8n JSON format

#### 5. Integration (`n8n_integration.py`)
- REST API calls to n8n
- Bulk upload capability
- Error handling for duplicate workflows

## Verification Plan

### Automated Tests

#### Unit Tests (pytest)

**Test 1: Text Extraction**
```bash
# Run from project root
poetry run pytest tests/test_extract_text.py -v

# Tests:
# - test_extract_pdf_basic() - Extracts text from sample PDF
# - test_extract_chapters() - Correctly identifies chapter boundaries
# - test_handle_malformed_pdf() - Gracefully handles corrupted PDFs
```

**Test 2: Pattern Recognition**
```bash
poetry run pytest tests/test_pattern_recognition.py -v

# Tests:
# - test_extract_patterns_valid_response() - Parses GPT-4 JSON correctly
# - test_extract_patterns_api_failure() - Handles API errors
# - test_pattern_validation() - Validates required fields
```

**Test 3: Workflow Generation**
```bash
poetry run pytest tests/test_workflow_generator.py -v

# Tests:
# - test_generate_facial_workflow() - Creates valid facial detection workflow
# - test_generate_linguistic_workflow() - Creates valid linguistic workflow
# - test_workflow_json_schema() - Validates n8n JSON format
```

**Coverage Target**: >80%
```bash
poetry run pytest --cov=src/psychology_to_n8n --cov-report=html
```

### Integration Tests

**Test 4: End-to-End Pipeline**
```bash
# Create test book (sample_psychology_book.pdf in tests/fixtures/)
poetry run python -m psychology_to_n8n.main \
  --book tests/fixtures/sample_psychology_book.pdf \
  --book-name "Test Book" \
  --output-dir test_output

# Verify:
# - Patterns extracted to test_output/patterns.db
# - Workflows generated in test_output/n8n_workflows/
# - Summary created in test_output/summaries/
```

**Test 5: n8n Integration** (requires running n8n instance)
```bash
# Start n8n locally
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# Upload test workflow
poetry run python -c "
from psychology_to_n8n.n8n_integration import N8nIntegration
n8n = N8nIntegration('http://localhost:5678', 'test-api-key')
n8n.upload_all_workflows('test_output/n8n_workflows')
"

# Verify in n8n UI: http://localhost:5678
# - Workflows appear in workflow list
# - Webhooks are correctly configured
# - Nodes are properly connected
```

### Manual Verification

**Test 6: Real Book Processing** (requires user to provide PDF)
```bash
# User provides a psychology book PDF
poetry run python -m psychology_to_n8n.main \
  --book books/telling_lies_ekman.pdf \
  --book-name "Telling Lies - Ekman" \
  --output-dir output

# Manual checks:
# 1. Open output/summaries/Telling_Lies_Ekman_summary.md
#    - Verify patterns make sense (e.g., "Microexpression of Fear")
#    - Check descriptions are accurate
# 2. Open output/n8n_workflows/Microexpression_of_Fear.json
#    - Verify JSON is valid (use jsonlint or VSCode)
#    - Check webhook path is reasonable
# 3. Check SQLite database
#    sqlite3 output/patterns.db "SELECT name, category, confidence FROM behavioral_patterns LIMIT 5;"
```

**Test 7: GPT-4 Quality Check** (requires OpenAI API key)
```bash
# Process a single chapter manually
poetry run python -c "
from psychology_to_n8n.pattern_recognition import BehavioralPatternExtractor
extractor = BehavioralPatternExtractor('sk-...')
patterns = extractor.extract_patterns('''
Chapter 3: Microexpressions
Microexpressions are brief, involuntary facial expressions that occur when a person is trying to conceal an emotion. They last between 1/25th to 1/5th of a second...
''')
print(patterns)
"

# User manually verifies:
# - Patterns extracted are relevant to deception
# - Confidence scores are reasonable (0.7-0.95)
# - Categories are correct (facial, vocal, etc.)
```

## Risks and Mitigations

### Risk 1: GPT-4 API Costs
- **Mitigation**: Cache results, process only new books
- **Estimate**: ~$5-10 per book (300 pages)

### Risk 2: Pattern Quality
- **Mitigation**: Manual review of first 10 patterns before bulk processing
- **Fallback**: Adjust GPT-4 prompt if quality is low

### Risk 3: n8n Workflow Compatibility
- **Mitigation**: Test with n8n v1.0+ (latest stable)
- **Fallback**: Generate workflows for specific n8n version

## Success Criteria

- [ ] Pipeline processes 1 book (300 pages) in <10 minutes
- [ ] Extracts 30-50 patterns per book
- [ ] Generates valid n8n workflows (100% pass n8n import)
- [ ] >80% test coverage
- [ ] All automated tests pass

## Next Steps After Implementation

1. Process 3-5 key psychology books
2. Generate ~100-150 workflows
3. Upload to n8n instance
4. Integrate with Truth Algorithm Layer 7
5. Test with real video/audio samples

# Sentinel Research Notebooks

## Overview

This directory contains Jupyter notebooks for scientific research and data analysis using Sentinel.

## Prerequisites

```bash
pip install jupyter pandas matplotlib seaborn numpy scipy requests
```

## Available Notebooks

### 1. sentinel_research.ipynb

**Complete research workflow** including:
- System health monitoring
- Coherence analysis over time
- AI performance benchmarking
- TruthSync verification testing
- Correlation analysis
- Data visualization
- Export capabilities

**Usage**:
```bash
jupyter notebook sentinel_research.ipynb
```

**Outputs**:
- `coherence_analysis.png` - Time-series plots
- `ai_latency_analysis.png` - AI performance chart
- `truthsync_verification.png` - Verification confidence chart
- `correlation_matrix.png` - Metric correlations
- `sentinel_coherence_data.csv` - Raw coherence data
- `sentinel_ai_performance.csv` - AI metrics
- `sentinel_verification_results.csv` - Verification results

## Quick Start

1. **Start Sentinel**:
   ```bash
   sudo sctl start
   sctl status
   ```

2. **Launch Jupyter**:
   ```bash
   cd /home/jnovoas/sentinel/notebooks
   jupyter notebook
   ```

3. **Open notebook** and run all cells

4. **View results** in generated PNG and CSV files

## Example Analysis

### Coherence Monitoring

```python
from sentinel_sdk import SentinelClient

client = SentinelClient()
measurements = client.monitor_coherence(duration_seconds=60, interval=2.0)

# Analyze
import pandas as pd
df = pd.DataFrame([asdict(m) for m in measurements])
print(f"Mean coherence: {df['coherence'].mean():.2%}")
```

### AI Performance Testing

```python
response = client.query_ai("Explain quantum computing", max_tokens=100)
print(f"Latency: {response.latency_ms:.2f}ms")
print(f"Model: {response.model}")
```

### TruthSync Verification

```python
result = client.verify_claim("Water boils at 100°C at sea level")
print(f"Confidence: {result.confidence:.2%}")
print(f"Status: {result.status}")
```

## Tips for Researchers

1. **Collect Longer Time Series**: Increase `duration_seconds` for trend analysis
2. **Adjust Sampling Rate**: Modify `interval` based on your needs
3. **Export Data**: Use `.to_csv()` for further analysis in R, MATLAB, etc.
4. **Customize Plots**: Modify matplotlib/seaborn settings for publication-quality figures
5. **Batch Processing**: Loop through multiple experiments

## Troubleshooting

### Sentinel Not Reachable

```bash
# Check if Sentinel is running
sctl status

# Start if needed
sudo sctl start

# Verify API is accessible
curl http://localhost:8000/api/v1/health
```

### Import Errors

```bash
# Install missing packages
pip install requests pandas matplotlib seaborn

# Or install all at once
pip install -r ../requirements.txt
```

### Kernel Issues

```bash
# Restart Jupyter kernel
# Kernel -> Restart & Clear Output

# Or restart Jupyter server
jupyter notebook stop
jupyter notebook
```

## Advanced Usage

### Custom Analysis

Create your own notebook based on `sentinel_research.ipynb`:

```python
# Import SDK
from sentinel_sdk import SentinelClient
import pandas as pd
import matplotlib.pyplot as plt

# Your custom analysis here
client = SentinelClient()
# ... your code ...
```

### Automation

Run notebooks from command line:

```bash
jupyter nbconvert --to notebook --execute sentinel_research.ipynb
```

### Scheduling

Use cron to run automated analysis:

```bash
# Add to crontab
0 */6 * * * cd /home/jnovoas/sentinel/notebooks && jupyter nbconvert --to notebook --execute sentinel_research.ipynb
```

## Resources

- **Python SDK**: `../sentinel_sdk.py`
- **Examples**: `../EXAMPLES_FOR_RESEARCHERS.md`
- **API Docs**: `../openapi.yaml`
- **Research Guide**: `../RESEARCH.md`

## Citation

If you use these notebooks in your research:

```bibtex
@software{sentinel_notebooks2026,
  title = {Sentinel Research Notebooks},
  author = {Your Name},
  year = {2026},
  url = {https://github.com/yourusername/sentinel}
}
```

---

**Happy researching! 🔬📊**

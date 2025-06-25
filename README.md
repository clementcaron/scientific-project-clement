# LLM Reasoning Framework Comparison

A focused experiment comparing three reasoning frameworks (ReAct, Chain-of-Thought, Tree-of-Thoughts) across three distinct task types.

## Overview

**Goal:** Compare how different reasoning approaches handle structured problem-solving across diverse domains.

**Tasks:**
- **Code Generation:** Implement Conway's Game of Life in Python
- **Itinerary Planning:** Create a European tour with constraints
- **Instruction Structuring:** Convert vague deployment steps into clear procedures

**Frameworks:**
- **ReAct:** Reasoning + Acting in interleaved steps
- **Chain-of-Thought:** Step-by-step logical reasoning
- **Tree-of-Thoughts:** Explore multiple reasoning paths

**Experiment Design:** 1 task per type × 3 frameworks × 3 runs = 9 experiments total

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.template .env
# Edit .env with your API keys (at least one required)

# Verify setup
python check_setup.py
```

### 2. Run Experiments
```bash
# Quick test (recommended first)
python run_experiment.py --quick

# Full experiment (3 runs per framework)
python run_experiment.py

# With rate limiting (for free API tiers)
python run_experiment.py --rate-limited
```

### 3. Analyze Results
```bash
# Open the main analysis notebook
jupyter notebook experiment.ipynb
```

## Project Structure

```
├── experiment.ipynb           # Main analysis notebook
├── run_experiment.py         # Command-line experiment runner
├── check_setup.py           # Setup validation
├── agents/                  # Framework implementations
├── tasks/                   # Task definitions and validation
├── utils/                   # LLM management utilities
├── results/                 # Experiment outputs (JSON/CSV)
└── .env                     # API keys (create from .env.template)
```

## Results & Evaluation

**Automated Metrics:**
- Execution time and token usage
- Task-specific validation scores (0-100)
- Success rates across frameworks

**Manual Review:**
- Full LLM responses saved for qualitative analysis
- Reasoning step breakdown for each framework
- Comparative analysis of problem-solving approaches

**Output Files:**
- `results/experiment_results_TIMESTAMP.csv` - Summary data
- `results/detailed_results_TIMESTAMP.json` - Full responses
- Interactive visualizations in the notebook

## Rate Limiting

Rate limiting is **enabled by default** to prevent API quota issues:
- 60 seconds between frameworks
- 10 seconds between runs

**Disable rate limiting:**
```bash
python run_experiment.py --no-limit
```

**Custom delays:**
```bash
python run_experiment.py --framework-cooldown 30 --run-cooldown 5
```

## Supported Models

Available Google Gemini models:
- `gemini-2.0-flash-exp` (default)
- `gemini-2.0-flash-lite`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-1.5-pro`

Configure your preferred model in `.env`:
```bash
DEFAULT_MODEL=gemini-2.0-flash-exp
```

## Key Features

- **Simple & Focused:** One task per domain, clear evaluation criteria
- **Rate Limit Safe:** Built-in delays prevent API quota exhaustion
- **Comprehensive Output:** Both automated metrics and full response logs
- **Easy Analysis:** Jupyter notebook with visualizations and insights
- **Reproducible:** All parameters and results saved automatically

## Troubleshooting

**API Rate Limits:** Use `--rate-limited` flag or configure custom cooldowns
**Missing Dependencies:** Run `pip install -r requirements.txt`
**API Key Issues:** Check `.env` file format (no quotes around keys)
**Low Scores:** Review detailed responses in results files or notebook

## Example Output

```
Task: Conway's Game of Life (code_001)

  Framework: REACT
    Status: ✓ | Score: 85/100 | Time: 2.3s | Tokens: 892
    Answer: Here's my implementation of Conway's Game of Life...
    
  Framework: COT  
    Status: ✓ | Score: 78/100 | Time: 1.8s | Tokens: 654
    Answer: Let me think through this step by step...
    
  Framework: TOT
    Status: ✓ | Score: 91/100 | Time: 3.1s | Tokens: 1156
    Answer: I'll explore multiple approaches to this problem...
```

Built for clear insights into LLM reasoning patterns across diverse problem domains.

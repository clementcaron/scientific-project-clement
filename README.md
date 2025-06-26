# LLM Reasoning Framework Comparison

A clean, focused experiment comparing three reasoning frameworks (ReAct, Chain-of-Thought, Tree-of-Thoughts) across three distinct task types. This project provides a simple, maintainable framework for evaluating how different reasoning approaches handle structured problem-solving.

## 🎯 Overview

**Goal:** Compare how different reasoning frameworks perform across diverse problem domains with automated validation and comprehensive analysis.

### 📋 Tasks
- **Code Generation (`code_001`):** Implement Conway's Game of Life with complete, runnable Python code
- **Itinerary Planning (`itin_001`):** Create a European tour with budget and time constraints  
- **Procedure Structuring (`proc_001`):** Convert vague deployment steps into clear, actionable procedures

### 🧠 Reasoning Frameworks
- **ReAct:** Combines reasoning and action in iterative cycles
- **Chain-of-Thought (CoT):** Sequential step-by-step logical reasoning
- **Tree-of-Thoughts (ToT):** Explores multiple reasoning branches systematically

### 🔬 Experiment Design
- **Quick Mode:** 1 task per type × 3 frameworks × 1 run = 9 experiments
- **Full Mode:** 1 task per type × 3 frameworks × 3 runs = 27 experiments
- **Custom color scheme:** Each framework has consistent colors across all visualizations

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and navigate to project
git clone <repository-url>
cd scientific-project-clement

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.template .env
# Edit .env with your Google API key (required)

# Verify setup
python check_setup.py
```

### 2. Run Experiments
```bash
# Quick test - recommended first run (9 experiments)
python run_experiment.py --quick

# Full experiment with 3 runs per framework (27 experiments)  
python run_experiment.py

# Disable rate limiting for faster execution
python run_experiment.py --no-limit

# Custom model selection
python run_experiment.py --model gemini-2.0-flash-exp
```

### 3. Analyze Results
```bash
# Open the comprehensive analysis notebook
jupyter lab experiment.ipynb

# Or use Jupyter Notebook
jupyter notebook experiment.ipynb
```

## 📁 Project Structure

```
scientific-project-clement/
├── experiment.ipynb           # 📊 Main analysis & visualization notebook
├── run_experiment.py         # 🚀 Command-line experiment runner  
├── check_setup.py           # ✅ Setup validation script
├── project_info.sh          # 📋 Quick project overview
├── agents/                  # 🧠 Framework implementations
│   ├── __init__.py
│   ├── react.py            # ReAct framework
│   ├── cot.py              # Chain-of-Thought framework  
│   └── tot.py              # Tree-of-Thoughts framework
├── tasks/                   # 📝 Task definitions & validation
│   ├── __init__.py
│   ├── generators.py       # Task generation logic
│   └── validators.py       # Validation & scoring system
├── utils/                   # 🛠️ Core utilities
│   ├── __init__.py
│   ├── llm_utils.py        # LLM management & API calls
│   └── logging_utils.py    # Result logging & data structures
├── results/                 # 📈 Experiment outputs
│   ├── experiment_results.json    # Consolidated experiment data
│   ├── experiment_summary.csv     # Summary metrics table
│   ├── llm_responses.txt          # All LLM responses
│   └── experiment_YYYYMMDD_HHMMSS.log  # Timestamped run logs
├── best_code.py            # 🏆 Reference implementation for validation
├── best_procedure.md       # 🏆 Reference procedure for validation  
├── best_itinerary.md      # 🏆 Reference itinerary for validation
├── requirements.txt        # 📦 Python dependencies
├── .env.template          # 🔧 Environment configuration template
└── README.md              # 📚 This file
```

## 📊 Results & Evaluation

### Validation System
- **Reference-Based Scoring:** Compares outputs against gold standard references using multiple criteria
- **Task-Specific Metrics:** Code validation, itinerary constraints, procedure completeness
- **Execution Tracking:** Time, tokens used, reasoning steps, memory usage
- **Success Rate Analysis:** Pass/fail rates across frameworks and tasks

### Output Files
- **`experiment_results.json`** - Complete experiment data with full responses and metadata
- **`experiment_summary.csv`** - Summary metrics for quick analysis and spreadsheet import
- **`llm_responses.txt`** - All LLM responses in human-readable format
- **`experiment_YYYYMMDD_HHMMSS.log`** - Detailed execution logs with timestamps

### Analysis Notebook
The `experiment.ipynb` notebook provides:
- **📈 Performance Visualizations:** Score distributions, time comparisons, success rates
- **📊 Statistical Analysis:** ANOVA tests, pairwise comparisons, effect sizes
- **🔍 Response Analysis:** Length, structure, and quality correlations
- **🏆 Framework Rankings:** Overall and task-specific performance comparisons

## ⚙️ Configuration & Models

### Supported Models
This project focuses exclusively on **Google Gemini models**:
- `gemini-2.0-flash-lite` (default - fast and efficient)
- `gemini-2.0-flash-exp` (experimental features)
- `gemini-2.5-flash` (balanced performance)
- `gemini-2.5-flash-lite` (lightweight option)
- `gemini-1.5-pro` (highest quality)

### Environment Configuration
Edit `.env` to customize:
```bash
# Required API key
GOOGLE_API_KEY=your_google_api_key_here

# Model selection  
DEFAULT_MODEL=gemini-2.0-flash-lite

# Experiment parameters
TEMPERATURE=0.3               # Response creativity (0.0-1.0)
RUNS_PER_TASK=3              # Number of runs per framework-task combination

# Rate limiting (uncomment to customize)
# FRAMEWORK_COOLDOWN=60       # Seconds between frameworks
# RUN_COOLDOWN=10            # Seconds between individual runs
```

### Rate Limiting
**Rate limiting is ON by default** to prevent API quota exhaustion:
- 60 seconds between framework switches
- 10 seconds between individual runs
- Prevents hitting free tier limits

**Control rate limiting:**
```bash
# Use default rate limits (recommended)
python run_experiment.py

# Disable all rate limiting
python run_experiment.py --no-limit
```

## 🔧 Troubleshooting

### Common Issues & Solutions

**🔑 API Key Problems**
```bash
# Check API key format (no quotes needed)
cat .env | grep GOOGLE_API_KEY

# Verify setup
python check_setup.py
```

**📈 Low Validation Scores**
- Review full responses in `results/llm_responses.txt`
- Check detailed validation feedback in experiment logs
- Consider using more capable models (e.g., `gemini-2.5-flash`)

**📦 Missing Dependencies**
```bash
# Reinstall requirements
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

**📊 Notebook Issues**
```bash
# Install Jupyter if missing
pip install jupyter jupyterlab

# Restart kernel if variables seem stale
# Kernel > Restart & Clear Output in Jupyter
```

## 📋 Example Output

### Command Line Results
```
🧠 LLM REASONING FRAMEWORK COMPARISON
=====================================

🎯 Experiment Configuration:
   Model: gemini-2.0-flash-lite
   Tasks: 3 (code_001, itin_001, proc_001)  
   Frameworks: 3 (react, cot, tot)
   Runs per framework: 1 (Quick mode)
   Total experiments: 9

📝 Task: Conway's Game of Life (code_001)
----------------------------------------

  🔧 REACT Framework:
     Status: ✅ PASSED | Score: 85/100 | Time: 2.3s | Tokens: 892
     Reasoning: 5 steps | Memory: 8.2MB
     
  🔧 COT Framework:  
     Status: ✅ PASSED | Score: 78/100 | Time: 1.8s | Tokens: 654
     Reasoning: 4 steps | Memory: 7.9MB
     
  🔧 TOT Framework:
     Status: ✅ PASSED | Score: 91/100 | Time: 3.1s | Tokens: 1156
     Reasoning: 7 steps | Memory: 9.1MB

🏆 RESULTS SUMMARY:
   Best Overall: TOT (85.3 avg score)
   Most Efficient: COT (43.3 score/second)
   Most Consistent: REACT (±3.2 std dev)
   
📊 Files Generated:
   ✓ results/experiment_results.json (detailed data)
   ✓ results/experiment_summary.csv (metrics table)  
   ✓ results/llm_responses.txt (full responses)
   ✓ results/experiment_20250626_154330.log (execution log)
```

### Notebook Analysis Preview
The `experiment.ipynb` provides rich visualizations including:
- **Framework Performance Dashboard:** Score distributions, success rates, timing analysis
- **Task-Specific Breakdowns:** Heatmaps showing which frameworks excel at which tasks
- **Response Quality Analysis:** Length vs. quality correlations, structure analysis
- **Statistical Significance Testing:** ANOVA results, pairwise comparisons with effect sizes

## 🎓 Research Applications

This framework is designed for:
- **Academic Research:** Comparing reasoning approaches in controlled experiments
- **LLM Evaluation:** Benchmarking model performance across diverse problem types
- **Framework Development:** Testing new reasoning methods against established baselines
- **Educational Use:** Understanding how different reasoning strategies work in practice



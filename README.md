# LLM Reasoning Framework Comparison

A comprehensive Python environment for comparing three reasoning frameworks for LLM-based agents: **ReAct**, **Chain-of-Thought (CoT)**, and **Tree-of-Thoughts (ToT)**.

## Overview

This project evaluates reasoning frameworks across three distinct task types:
1. **Code Generation**: Implement Conway's Game of Life, Binary Search Trees, Text Analysis Tools
2. **Itinerary Planning**: Generate optimized travel routes with constraints
3. **Procedure Structuring**: Transform vague instructions into clear procedures

## Features

- 🤖 **Three Reasoning Frameworks**: ReAct, CoT, ToT implementations
- 📊 **Comprehensive Evaluation**: Token usage, execution time, validation scores
- 🎯 **Multiple Task Types**: 9 total tasks (3 per category)
- 🔬 **Statistical Analysis**: Multiple runs for consistency measurement
- 📈 **Visualization**: Interactive Streamlit dashboard and Jupyter analysis
- 🔧 **Flexible LLM Support**: Google Gemini, OpenAI, Mistral integration

## Project Structure

```
scientific-project-clement/
├── agents/                 # Reasoning framework implementations
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── react_agent.py     # ReAct implementation
│   ├── cot_agent.py       # Chain-of-Thought implementation
│   ├── tot_agent.py       # Tree-of-Thoughts implementation
│   └── factory.py         # Agent factory
├── tasks/                  # Task definitions and validation
│   ├── __init__.py
│   ├── task_definitions.py # Task specifications
│   └── validators.py       # Output validation logic
├── utils/                  # Utilities and logging
│   ├── __init__.py
│   ├── logging_utils.py    # Experiment logging
│   └── llm_utils.py        # LLM configuration
├── results/                # Experiment results (created automatically)
├── run_experiment.py       # Main experiment runner
├── streamlit_app.py       # Interactive dashboard
├── framework_comparison_analysis.ipynb  # Analysis notebook
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
└── README.md              # This file
```

## Quick Start

### 1. Installation

```bash
# Clone and navigate to the project directory
git clone scientific-project-clement
cd scientific-project-clement

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and add your API keys:

```bash
cp .env.template .env
```

Edit `.env` with your API keys:
```
GOOGLE_API_KEY=your_google_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

DEFAULT_MODEL=gemini-2.0-flash-exp
TEMPERATURE=0.3
MAX_TOKENS=2048
RUNS_PER_TASK=3

# Rate limiting for free/limited API plans
FRAMEWORK_COOLDOWN=0    # Seconds between frameworks (0 = no delay)
RUN_COOLDOWN=0         # Seconds between runs (0 = no delay)
```

### 3. Run Experiments

#### Command Line (Recommended)
```bash
# Full experiment (all frameworks, all tasks, 3 runs each)
python run_experiment.py

# Quick test (1 task per type, 1 run each)
python run_experiment.py --quick

# Rate-limited mode (for free API tiers)
python run_experiment.py --rate-limited

# Custom cooldowns
python run_experiment.py --framework-cooldown 60 --run-cooldown 10

# Specific frameworks only
python run_experiment.py --frameworks react cot

# Specific task types only
python run_experiment.py --task-types code_generation
```

#### Rate Limiting for Free API Tiers
If you're using free tier APIs (like Google Gemini free tier), use rate limiting to avoid quota errors:

```bash
# Preset for free tiers (60s between frameworks, 10s between runs)
python run_experiment.py --rate-limited

# Manual cooldown settings
python run_experiment.py --framework-cooldown 60 --run-cooldown 10

# Environment variables (set in .env)
FRAMEWORK_COOLDOWN=60
RUN_COOLDOWN=10
```

#### Jupyter Notebook
Open `framework_comparison_analysis.ipynb` and run all cells for interactive analysis.

### 4. View Results

#### Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```

#### Results Files
Results are automatically saved to the `results/` directory:
- `results_YYYYMMDD_HHMMSS.json` - Detailed results
- `results_summary_YYYYMMDD_HHMMSS.csv` - Summary statistics
- `summary_report_YYYYMMDD_HHMMSS.json` - Analysis report

## Reasoning Frameworks

### ReAct (Reasoning + Acting)
Alternates between reasoning about the problem and taking specific actions:
```
Thought: [Reasoning about what to do next]
Action: [Specific action being taken]
Observation: [What was learned from the action]
```

### Chain-of-Thought (CoT)
Uses linear step-by-step reasoning:
```
Step 1: [Understand the problem]
Step 2: [Break down into components]
Step 3: [Plan approach]
...
Final Solution: [Complete answer]
```

### Tree-of-Thoughts (ToT)
Explores multiple reasoning paths and selects the best:
```
Approach 1: [First method]
Approach 2: [Second method]
Approach 3: [Third method]

[Evaluate each approach]
[Select best approach]
[Execute selected approach]
```

## Task Categories

### Code Generation Tasks
1. **Conway's Game of Life**: Implement the cellular automaton with proper rules
2. **Binary Search Tree**: Complete BST with insert, search, delete, traversal
3. **Text Analysis Tool**: File processing with statistics and CLI interface

### Itinerary Planning Tasks
1. **European City Tour**: 7-day multi-city trip with budget constraints
2. **Business Trip Optimization**: 3-day trip optimizing for meetings and travel time
3. **Family Vacation Planning**: 5-day Orlando trip with special requirements

### Procedure Structuring Tasks
1. **Software Deployment Process**: Transform vague deployment instructions
2. **Customer Onboarding Process**: Structure customer onboarding workflow
3. **Emergency Response Protocol**: Organize emergency response procedures

## Evaluation Metrics

- **Success Rate**: Percentage of successful task completions
- **Validation Score**: Automated scoring based on task requirements (0-100)
- **Token Usage**: Number of tokens consumed by the LLM
- **Execution Time**: Time taken to complete the task
- **Memory Usage**: Peak memory consumption during execution
- **Reasoning Steps**: Number of intermediate reasoning steps
- **Consistency**: Standard deviation across multiple runs

## Supported LLMs

- **Google Gemini**: `gemini-2.0-flash-exp`, `gemini-1.5-pro`
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`
- **Mistral**: `mistral-small`, `mistral-medium`

## Extending the Framework

### Adding New Reasoning Frameworks

1. Create a new agent class inheriting from `BaseAgent`:
```python
class MyAgent(BaseAgent):
    def get_framework_prompt(self, task_prompt: str, task_type: str) -> str:
        # Return framework-specific prompt
        
    def _extract_reasoning_steps(self, response: str) -> List[str]:
        # Extract reasoning steps from response
        
    def _extract_final_answer(self, response: str) -> str:
        # Extract final answer from response
```

2. Register the agent:
```python
AgentFactory.register_agent('my_framework', MyAgent)
```

### Adding New Task Types

1. Add tasks in `TaskGenerator`:
```python
@staticmethod
def get_my_task_type() -> List[Task]:
    return [Task(...)]
```

2. Add validation logic in `TaskValidator`:
```python
@staticmethod
def validate_my_task_type(task: Task, output: str) -> Tuple[bool, List[str], float]:
    # Validation logic
```

## Analysis Features

### Statistical Analysis
- Framework performance comparison
- Task type difficulty analysis
- Consistency measurements
- Token efficiency analysis

### Visualizations
- Success rate comparisons
- Performance metric distributions
- Task-specific performance
- Consistency vs accuracy plots

### Interactive Dashboard
- Real-time filtering and exploration
- Downloadable results
- Comparative analysis tools
- Detailed result inspection

## Research Applications

This framework is designed for:
- **Comparative Studies**: Systematic comparison of reasoning approaches
- **Framework Development**: Testing new reasoning methodologies
- **Task Analysis**: Understanding task-specific performance patterns
- **LLM Evaluation**: Assessing model capabilities across reasoning styles

## Performance Optimization

- **Batch Processing**: Run multiple experiments efficiently
- **Caching**: Avoid redundant LLM calls
- **Async Execution**: Parallel processing support
- **Resource Monitoring**: Memory and token usage tracking

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in `.env`
2. **Rate Limit Errors**: Use `--rate-limited` flag or set cooldown parameters
3. **Import Errors**: Check that all dependencies are installed
4. **Memory Issues**: Reduce `runs_per_task` or use lighter models
5. **Timeout Errors**: Increase timeout settings or use faster models

### Rate Limiting Solutions

**Problem**: "429 You exceeded your current quota" or similar rate limit errors

**Solutions**:
```bash
# Use the rate-limited preset
python run_experiment.py --rate-limited

# Set custom cooldowns (in seconds)
python run_experiment.py --framework-cooldown 60 --run-cooldown 10

# For very strict limits, increase cooldowns
python run_experiment.py --framework-cooldown 120 --run-cooldown 20

# Run fewer tasks at once
python run_experiment.py --quick --rate-limited
```

**API-Specific Recommendations**:
- **Google Gemini Free**: `--framework-cooldown 60 --run-cooldown 10` (10 requests/minute limit)
- **OpenAI Free Tier**: `--framework-cooldown 20 --run-cooldown 5` 
- **Mistral API**: `--framework-cooldown 30 --run-cooldown 5`

### Debug Mode

Run with verbose logging:
```bash
python run_experiment.py --quick --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Include tests and documentation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{llm_reasoning_framework_comparison,
  title={LLM Reasoning Framework Comparison},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/scientific-project-clement}
}
```

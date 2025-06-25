# Rate Limiting Guide for LLM Framework Comparison

## Problem Solved ✅

You experienced Google Gemini API rate limit errors (429 quota exceeded) after just a few requests. The free tier allows only **10 requests per minute**, which was quickly exceeded when running multiple framework comparisons.

## New Features Added

### 1. Cooldown Parameters
- **Framework Cooldown**: Wait time between testing different frameworks (ReAct → CoT → ToT)
- **Run Cooldown**: Wait time between multiple runs of the same task

### 2. Command Line Options
```bash
# Quick rate-limited mode (60s between frameworks, 10s between runs)
python run_experiment.py --rate-limited

# Custom cooldowns
python run_experiment.py --framework-cooldown 60 --run-cooldown 10

# Combine with other options
python run_experiment.py --quick --rate-limited --frameworks react cot
```

### 3. Environment Variables
Add to your `.env` file:
```
FRAMEWORK_COOLDOWN=60    # 1 minute between frameworks
RUN_COOLDOWN=10         # 10 seconds between runs
```

### 4. Automatic Detection
- The system detects rate limit errors (429, quota exceeded, etc.)
- Provides suggestions for appropriate cooldown settings
- Shows model-specific recommendations at startup

## Usage Examples for Your Situation

### For Google Gemini Free Tier (10 requests/minute)
```bash
# Recommended: 1 minute between frameworks, 10 seconds between runs
python run_experiment.py --rate-limited

# Conservative: 2 minutes between frameworks
python run_experiment.py --framework-cooldown 120 --run-cooldown 15

# Quick test only (3 tasks, 1 run each)
python run_experiment.py --quick --rate-limited
```

### Timeline Example
Without cooldown:
- ❌ Framework 1: Request 1, 2, 3 (3 requests in 10 seconds → rate limit)

With cooldown (`--rate-limited`):
- ✅ Framework 1: Request 1 → wait 60s → Framework 2: Request 2 → wait 60s → Framework 3: Request 3

## Configuration Options

### 1. Command Line Arguments
```bash
--rate-limited              # Preset: 60s framework, 10s run cooldown
--framework-cooldown 60     # Custom framework cooldown (seconds)
--run-cooldown 10          # Custom run cooldown (seconds)
```

### 2. Environment Variables (.env file)
```bash
FRAMEWORK_COOLDOWN=60      # Default framework cooldown
RUN_COOLDOWN=10           # Default run cooldown
```

### 3. Programmatic (in Jupyter notebook)
```python
runner = ExperimentRunner(
    framework_cooldown=60.0,  # 1 minute between frameworks
    run_cooldown=10.0        # 10 seconds between runs
)
```

## Visual Progress Indicators

The system now shows cooldown progress:
```
Framework: REACT
  ⏱️  Framework cooldown: 60s
  Run 1/3 [1/9] - ✓ Score: 75
  ⏱️  Run cooldown: 10s  
  Run 2/3 [2/9] - ✓ Score: 82
```

## Recommended Settings by API

| API Provider | Framework Cooldown | Run Cooldown | Max Requests/Min |
|-------------|-------------------|--------------|------------------|
| Google Gemini Free | 60s | 10s | 10 |
| OpenAI Free Tier | 20s | 5s | ~30 |
| OpenAI Paid | 10s | 2s | 3500+ |
| Mistral API | 30s | 5s | Varies |

## Quick Start for Your Case

1. **Set up your .env file:**
```bash
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

2. **Run with rate limiting:**
```bash
# Quick test (1 task per type, rate limited)
python run_experiment.py --quick --rate-limited

# Full experiment (all tasks, rate limited)
python run_experiment.py --rate-limited
```

3. **Monitor progress:**
The system will show cooldown timers and prevent rate limit errors.

## Advanced Usage

### Test Only Specific Frameworks (faster)
```bash
# Test only ReAct and CoT (skip ToT)
python run_experiment.py --frameworks react cot --rate-limited

# Test only code generation tasks
python run_experiment.py --task-types code_generation --rate-limited
```

### Adjust for Stricter Limits
```bash
# Very conservative (2 minutes between frameworks)
python run_experiment.py --framework-cooldown 120 --run-cooldown 20
```

## Expected Timeline

With `--rate-limited` on full experiment:
- **3 frameworks × 3 task types × 3 runs = 27 total requests**
- **With 60s framework cooldown: ~18 minutes total**
- **Without cooldown: Rate limit errors after ~1 minute**

## Files Modified

1. `run_experiment.py` - Added cooldown logic and CLI arguments
2. `.env.template` - Added cooldown environment variables  
3. `README.md` - Updated documentation with rate limiting guide
4. Created `test_rate_limiting.py` - Test script for cooldown features

## Next Steps

1. Try the quick test: `python run_experiment.py --quick --rate-limited`
2. If successful, run full experiment: `python run_experiment.py --rate-limited`
3. Adjust cooldowns if you still hit rate limits
4. Use `--frameworks react cot` to test fewer frameworks initially

This should completely solve your rate limiting issues! 🎉

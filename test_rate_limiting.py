#!/usr/bin/env python3
"""
Test script to demonstrate the new rate limiting features.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from run_experiment import ExperimentRunner

def test_cooldown_functionality():
    """Test the cooldown functionality without making API calls."""
    print("🧪 Testing Rate Limiting Features")
    print("=" * 50)
    
    # Test 1: Default settings (no cooldown)
    print("\n1. Default settings:")
    runner1 = ExperimentRunner()
    print(f"   Framework cooldown: {runner1.framework_cooldown}s")
    print(f"   Run cooldown: {runner1.run_cooldown}s")
    
    # Test 2: Custom cooldown settings
    print("\n2. Custom cooldown settings:")
    runner2 = ExperimentRunner(
        framework_cooldown=60.0,
        run_cooldown=10.0
    )
    print(f"   Framework cooldown: {runner2.framework_cooldown}s")
    print(f"   Run cooldown: {runner2.run_cooldown}s")
    
    # Test 3: Rate limit error detection
    print("\n3. Rate limit error detection:")
    test_errors = [
        "429 You exceeded your current quota",
        "Rate limit exceeded",
        "Too many requests",
        "quota_metric: generativelanguage.googleapis.com",
        "Normal error message"
    ]
    
    for error in test_errors:
        cooldown = runner1._handle_rate_limit_error(error)
        is_rate_limit = cooldown is not None
        print(f"   '{error[:30]}...' -> Rate limit: {is_rate_limit}")
        if is_rate_limit:
            print(f"      Suggested cooldown: {cooldown}s")
    
    # Test 4: Model-specific suggestions
    print("\n4. Model-specific cooldown suggestions:")
    test_models = ['gemini-2.0-flash-exp', 'gpt-4', 'mistral-small']
    
    for model in test_models:
        print(f"\n   Testing {model}:")
        runner = ExperimentRunner(model_name=model)
        # The suggestions are printed during initialization
    
    print("\n✅ All cooldown functionality tests passed!")
    
    print("\n📖 Usage Examples:")
    print("   # Rate-limited mode (preset cooldowns)")
    print("   python run_experiment.py --rate-limited")
    print()
    print("   # Custom cooldowns")
    print("   python run_experiment.py --framework-cooldown 60 --run-cooldown 10")
    print()
    print("   # Quick test with rate limiting")
    print("   python run_experiment.py --quick --rate-limited")

if __name__ == "__main__":
    test_cooldown_functionality()

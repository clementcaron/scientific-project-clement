#!/usr/bin/env python3
"""
Simple setup validation for LLM Reasoning Framework Comparison.
Checks dependencies, API keys, and basic functionality.
"""
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required = ['langchain', 'langchain_google_genai', 'pandas', 'matplotlib', 'dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    return missing

def check_env_setup():
    """Check environment configuration."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.template .env")
        return False
    
    print("✅ .env file exists")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and not api_key.startswith('your_'):
        print(f"✅ Google Gemini API key configured")
        configured = True
    else:
        print(f"❌ Google Gemini API key not configured")
        configured = False
    
    if not configured:
        print("⚠️  Google API key not configured. Please add GOOGLE_API_KEY to your .env file.")
        return False
    
    return True

def test_basic_functionality():
    """Test basic LLM functionality."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Try to create a simple LLM instance
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key and not google_key.startswith('your_'):
            from langchain_google_genai import GoogleGenerativeAI
            llm = GoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=google_key,
                temperature=0.3
            )
            print("✅ LLM initialization successful")
            return True
        else:
            print("⚠️  Skipping LLM test (no API key)")
            return False
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def main():
    """Run all setup checks."""
    print("🔍 LLM Reasoning Framework Setup Check")
    print("=" * 40)
    
    # Check dependencies
    print("\n📦 Dependencies:")
    missing = check_dependencies()
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    # Check environment
    print("\n🔧 Environment:")
    env_ok = check_env_setup()
    
    # Test functionality
    print("\n🧪 Functionality:")
    func_ok = test_basic_functionality()
    
    # Summary
    print("\n" + "=" * 40)
    if missing:
        print("❌ Setup incomplete - install missing packages")
    elif not env_ok:
        print("⚠️  Setup partial - configure API keys for full functionality")
    elif func_ok:
        print("✅ Setup complete - ready to run experiments!")
    else:
        print("⚠️  Setup complete - API functionality not tested")
    
    print("\n🚀 Next steps:")
    print("   jupyter notebook experiment.ipynb")
    print("   # or")
    print("   python run_experiment.py --quick")
    
    return True

if __name__ == "__main__":
    main()

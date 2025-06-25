#!/usr/bin/env python3
"""
Setup verification script for the LLM Reasoning Framework Comparison project.
"""
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'langchain',
        'pandas', 
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',
        'streamlit',
        'psutil',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return missing_packages

def check_project_structure():
    """Check if all project files are in place."""
    required_files = [
        'agents/__init__.py',
        'agents/base_agent.py',
        'agents/react_agent.py',
        'agents/cot_agent.py',
        'agents/tot_agent.py',
        'agents/factory.py',
        'tasks/__init__.py',
        'tasks/task_definitions.py',
        'tasks/validators.py',
        'utils/__init__.py',
        'utils/logging_utils.py',
        'utils/llm_utils.py',
        'run_experiment.py',
        'streamlit_app.py',
        'framework_comparison_analysis.ipynb',
        'requirements.txt',
        '.env.template',
        'README.md'
    ]
    
    project_root = Path(__file__).parent
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def check_environment():
    """Check environment configuration."""
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    print(f"Environment template: {'✅' if env_template.exists() else '❌'}")
    print(f"Environment file: {'✅' if env_file.exists() else '⚠️  Not created (copy from .env.template)'}")
    
    # Check for API keys (if .env exists)
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = ['GOOGLE_API_KEY', 'OPENAI_API_KEY', 'MISTRAL_API_KEY']
        for key in api_keys:
            value = os.getenv(key)
            status = "✅" if value and value != "your_key_here" else "⚠️"
            print(f"  {key}: {status}")

def main():
    """Run all setup checks."""
    print("🔍 LLM Reasoning Framework Comparison - Setup Verification")
    print("=" * 60)
    
    print("\n📦 Checking Dependencies:")
    missing_deps = check_dependencies()
    
    print("\n📁 Checking Project Structure:")
    missing_files = check_project_structure()
    
    print("\n🔧 Checking Environment:")
    check_environment()
    
    print("\n" + "=" * 60)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Run: pip install -r requirements.txt")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
    
    if not missing_deps and not missing_files:
        print("✅ Setup verification complete! All components are in place.")
        print("\n📋 Next Steps:")
        print("1. Copy .env.template to .env and add your API keys")
        print("2. Run quick test: python run_experiment.py --quick")
        print("3. Open Jupyter notebook: framework_comparison_analysis.ipynb")
        print("4. Launch dashboard: streamlit run streamlit_app.py")
    else:
        print("⚠️  Setup incomplete. Please address the issues above.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
System Check Script

Verifies that all components are properly installed and configured.
"""

import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    return True

def check_dependencies():
    print_header("Checking Dependencies")
    required = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "requests"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def check_ollama():
    print_header("Checking Ollama")
    try:
        from llm.client import LLMClient
        client = LLMClient()
        if client.is_available():
            print("✓ Ollama is running")
            print("✓ Model: qwen2.5:14b-instruct-q4_K_M")
            return True
        else:
            print("❌ Ollama is not responding")
            print("\nStart Ollama with:")
            print("  ollama serve")
            print("\nEnsure model is pulled:")
            print("  ollama pull qwen2.5:14b-instruct-q4_K_M")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_database():
    print_header("Checking Database")
    try:
        from memory.structured_memory import StructuredMemory
        memory = StructuredMemory()
        
        # Check if database file exists
        if os.path.exists(memory.db_path):
            print(f"✓ Database exists: {memory.db_path}")
        else:
            print(f"⚠️  Database will be created: {memory.db_path}")
        
        # Try to get metrics
        metrics = memory.get_metrics()
        print(f"✓ Database accessible")
        print(f"  Total interactions: {metrics.get('total_interactions', 0)}")
        print(f"  Learned patterns: {metrics.get('learned_patterns_count', 0)}")
        print(f"  Defender rules: {metrics.get('defender_rules_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_agents():
    print_header("Checking Agents")
    try:
        from defender_agent.agent import DefenderAgent
        from attacker_agent.agent import AttackerAgent
        from evaluator_agent.agent import EvaluatorAgent
        from learning_agent.agent import LearningAgent
        from chatbot.assistant import ProtectedAssistant
        
        print("✓ DefenderAgent")
        print("✓ AttackerAgent")
        print("✓ EvaluatorAgent")
        print("✓ LearningAgent")
        print("✓ ProtectedAssistant")
        
        return True
    except Exception as e:
        print(f"❌ Agent import error: {e}")
        return False

def check_orchestration():
    print_header("Checking Orchestration")
    try:
        from orchestration.graph import DefenseGraph
        print("✓ DefenseGraph")
        
        # Try to create instance
        graph = DefenseGraph(mode="PROTECTION")
        print("✓ DefenseGraph instantiation")
        
        return True
    except Exception as e:
        print(f"❌ Orchestration error: {e}")
        return False

def check_data_files():
    print_header("Checking Data Files")
    
    files = [
        "data/mock_company_data.json",
        "llm/prompts.py",
        "memory/schema.py"
    ]
    
    all_exist = True
    for file_path in files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Adaptive Multi-Agent LLM Defense System".center(58) + "║")
    print("║" + "  System Check".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Ollama", check_ollama),
        ("Database", check_database),
        ("Agents", check_agents),
        ("Orchestration", check_orchestration),
        ("Data Files", check_data_files)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! System is ready.")
        print("\nNext steps:")
        print("  1. Run demo: python run_e2e_demo.py")
        print("  2. Run tests: pytest tests/test_end_to_end.py -v -s")
        print("  3. Start UI: streamlit run streamlit_app.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

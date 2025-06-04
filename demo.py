"""
Demo script for OdyTest - Model Evaluation Suite
Showcases the main functionality and usage patterns
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when used as module)
    from .test_cases import get_test_summary
    from .prompt_manager import get_available_variants
    from .config import get_model_list, get_model_config
except ImportError:
    # Fall back to direct imports (when run as script)
    from test_cases import get_test_summary
    from prompt_manager import get_available_variants
    from config import get_model_list, get_model_config # type: ignore


def demo_test_suite_overview():
    """Demonstrate test suite overview"""
    print("\n📊 DEMO: Test Suite Overview")
    print("=" * 50)
    
    summary = get_test_summary()
    
    print(f"📋 Test Suite Summary:")
    print(f"   Total Cases: {summary['total_cases']}")
    
    print(f"\n🌍 Languages:")
    for lang, count in summary['by_language'].items():
        print(f"   {lang}: {count} test cases")
    
    print(f"\n📊 Difficulty Levels:")
    for diff, count in summary['by_difficulty'].items():
        print(f"   {diff}: {count} test cases")
    
    print(f"\n📂 Categories:")
    for cat, count in summary['by_category'].items():
        print(f"   {cat}: {count} test cases")

def demo_model_configurations():
    """Demonstrate model configuration display"""
    print("\n🤖 DEMO: Model Configurations")
    print("=" * 50)
    
    models = get_model_list()
    print(f"Available Models: {len(models)}")
    
    for model_key in models:
        config = get_model_config(model_key)
        print(f"\n📋 {model_key}:")
        print(f"   Name: {config.name}")
        print(f"   Description: {config.description}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Top-p: {config.top_p}")
        print(f"   Timeout: {config.timeout}s")
        print(f"   Max Retries: {config.max_retries}")

def demo_prompt_variants():
    """Demonstrate prompt variant information"""
    print("\n📝 DEMO: Prompt Variants")
    print("=" * 50)
    
    variants = get_available_variants()
    print(f"Available Prompt Variants: {len(variants)}")
    
    for name, description in variants.items():
        print(f"\n🔹 {name}:")
        print(f"   {description}")

def demo_usage_examples():
    """Demonstrate usage examples"""
    print("\n💡 DEMO: Usage Examples")
    print("=" * 50)
    
    print("🔧 Command Line Usage:")
    print()
    print("# Test single model with production prompt")
    print("python test_single_model.py qwen3_1_7b")
    print()
    print("# Test with different prompt variant")
    print("python test_single_model.py gemma3_1b --prompt multilingual")
    print()
    print("# Run sequential tests for all models")
    print("python run_sequential_tests.py")
    print()
    print("# Test specific models only")
    print("python run_sequential_tests.py --models qwen3_1_7b gemma3_1b")
    print()
    print("# Generate report from existing results")
    print("python run_sequential_tests.py --generate-report-only")
    
    print("\n🐍 Programmatic Usage:")
    print()
    print("from test_single_model import test_single_model")
    print("from run_sequential_tests import SequentialTestRunner")
    print()
    print("# Test single model")
    print("result_file = test_single_model('qwen3_1_7b', 'production')")
    print()
    print("# Run sequential tests")
    print("runner = SequentialTestRunner('multilingual')")
    print("success = runner.run_complete_evaluation(['qwen3_1_7b', 'gemma3_1b'])")

def demo_workflow():
    """Demonstrate typical testing workflow"""
    print("\n🔄 DEMO: Typical Testing Workflow")
    print("=" * 50)
    
    print("1. 📋 Review available models and test cases")
    print("   python test_single_model.py --list-models")
    print("   python test_single_model.py --list-prompts")
    print()
    
    print("2. 🔧 Load first model in Ollama")
    print("   ollama pull qwen3:1.7b")
    print()
    
    print("3. 🧪 Run tests for first model")
    print("   python test_single_model.py qwen3_1_7b")
    print()
    
    print("4. 🔄 Switch to next model")
    print("   ollama rm qwen3:1.7b")
    print("   ollama pull gemma3:1b")
    print()
    
    print("5. 🧪 Run tests for second model")
    print("   python test_single_model.py gemma3_1b")
    print()
    
    print("6. 📊 Generate comparative analysis")
    print("   python run_sequential_tests.py --generate-report-only")
    print()
    
    print("7. 🎯 Review results and select best model for production")

def demo_output_structure():
    """Demonstrate output file structure"""
    print("\n📁 DEMO: Output File Structure")
    print("=" * 50)
    
    print("📂 tests/odytest/results/")
    print("├── qwen3_1_7b_production_20250603_143000.json")
    print("├── gemma3_1b_production_20250603_143100.json")
    print("├── qwen3_0_6b_production_20250603_143200.json")
    print("└── comparative_analysis_20250603_143300.json")
    print()
    
    print("📋 Individual Model Results contain:")
    print("   • Test metadata (model, prompt, timestamp)")
    print("   • Summary statistics (accuracy, timing, confidence)")
    print("   • Detailed results for each test case")
    print("   • Language and difficulty breakdowns")
    print()
    
    print("📊 Comparative Analysis contains:")
    print("   • Model rankings by different criteria")
    print("   • Performance comparison matrix")
    print("   • Language-specific recommendations")
    print("   • Production deployment guidance")

def main():
    """Run the complete demo"""
    print("🚀 ODYTEST DEMONSTRATION")
    print("=" * 80)
    print("Welcome to the OdyTest Model Evaluation Suite demonstration!")
    print("This demo showcases the main features and usage patterns.")
    print("=" * 80)
    
    try:
        demo_test_suite_overview()
        demo_model_configurations()
        demo_prompt_variants()
        demo_usage_examples()
        demo_workflow()
        demo_output_structure()
        
        print("\n🎉 DEMO COMPLETE")
        print("=" * 50)
        print("The OdyTest suite is ready for model evaluation!")
        print("Start by running: python test_single_model.py --list-models")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is normal if dependencies are not installed.")
        print("The demo shows the intended functionality.")

if __name__ == "__main__":
    main()

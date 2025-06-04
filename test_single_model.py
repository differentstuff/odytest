"""
Single Model Test Runner for OdyTest - Model Evaluation Suite
Tests one model at a time for fair comparison using Ollama client
"""

import argparse
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when used as module)
    from .config import get_model_config, get_model_list
    from .test_cases import get_test_cases, get_test_summary
    from .model_evaluator import create_evaluator
    from .results_manager import save_results
    from .prompt_manager import get_available_variants
    from .test_ollama_library import OllamaError
except ImportError:
    # Fall back to direct imports (when run as script)
    from config import get_model_config, get_model_list # type: ignore
    from test_cases import get_test_cases, get_test_summary
    from model_evaluator import create_evaluator
    from results_manager import save_results
    from prompt_manager import get_available_variants
    from test_ollama_library import OllamaError

def test_single_model(model_key: str, prompt_variant: str = "production") -> Optional[str]:
    """
    Test a single model with specified prompt variant
    
    Args:
        model_key: Model configuration key
        prompt_variant: Prompt variant to use
        
    Returns:
        Path to results file if successful, None otherwise
    """
    
    print(f"\n🚀 OdyTest - Single Model Evaluation")
    print("=" * 60)
    print(f"Model: {model_key}")
    print(f"Prompt Variant: {prompt_variant}")
    
    try:
        # Get model configuration
        model_config = get_model_config(model_key)
        print(f"📋 Model Config: {model_config.description}")
        
        # Get test cases
        test_cases = get_test_cases()
        test_summary = get_test_summary()
        
        print(f"\n📊 Test Suite Summary:")
        print(f"   Total Cases: {test_summary['total_cases']}")
        print(f"   Languages: {list(test_summary['by_language'].keys())}")
        print(f"   Difficulties: {list(test_summary['by_difficulty'].keys())}")
        print(f"   Categories: {list(test_summary['by_category'].keys())}")
        
        # Create evaluator
        evaluator = create_evaluator(model_config)
        
        # Run tests
        results = evaluator.execute_test_suite(test_cases, prompt_variant)
        
        if not results:
            print("❌ No results generated - model may not be available")
            return None
        
        # Generate summary statistics
        summary_stats = evaluator.generate_summary_stats(results)
        
        # Print immediate summary
        print(f"\n📈 Test Results Summary:")
        print(f"   Success Rate: {summary_stats['success_rate']:.1%}")
        print(f"   JSON Validity: {summary_stats['json_validity_rate']:.1%}")
        print(f"   Intent Accuracy: {summary_stats['intent_accuracy_rate']:.1%}")
        
        if 'timing' in summary_stats:
            timing = summary_stats['timing']
            print(f"   Avg Inference Time: {timing['avg_inference_time']:.2f}s")
            print(f"   Min/Max Time: {timing['min_inference_time']:.2f}s / {timing['max_inference_time']:.2f}s")
        
        if 'confidence' in summary_stats:
            confidence = summary_stats['confidence']
            print(f"   Avg Confidence: {confidence['avg_confidence']:.2f}")
        
        # Language breakdown
        print(f"\n🌍 Language Performance:")
        for lang, data in summary_stats['by_language'].items():
            print(f"   {lang}: {data['accuracy']:.1%} ({data['total']} tests)")
        
        # Difficulty breakdown
        print(f"\n📊 Difficulty Performance:")
        for diff, data in summary_stats['by_difficulty'].items():
            print(f"   {diff}: {data['accuracy']:.1%} ({data['total']} tests)")
        
        # Save results
        results_file = save_results(model_config.name, prompt_variant, results, summary_stats)
        
        print(f"\n✅ Testing completed successfully!")
        print(f"📁 Results saved to: {results_file}")
        
        return results_file
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None

def main():
    """Main entry point for single model testing"""
    
    parser = argparse.ArgumentParser(
        description="Test a single model for LLM performance evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_single_model.py qwen3_4b
  python test_single_model.py deepseek_r1 --prompt multilingual
  python test_single_model.py llama_3_3_8b --prompt chain_of_thought
        """
    )
    
    parser.add_argument(
        "model",
        nargs='?',
        choices=get_model_list(),
        help="Model to test"
    )
    
    parser.add_argument(
        "--prompt",
        choices=list(get_available_variants().keys()),
        default="production",
        help="Prompt variant to use (default: production)"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List available prompt variants and exit"
    )
    
    args = parser.parse_args()
    
    # Handle list commands
    if args.list_models:
        print("Available models:")
        for key in get_model_list():
            config = get_model_config(key)
            print(f"  {key}: {config.description}")
        return
    
    if args.list_prompts:
        print("Available prompt variants:")
        for name, description in get_available_variants().items():
            print(f"  {name}: {description}")
        return
    
    # Validate model argument is provided
    if not args.model:
        parser.error("Model argument is required when not using --list-models or --list-prompts")
    
    # Run test
    result_file = test_single_model(args.model, args.prompt)
    
    if result_file:
        print(f"\n🎉 Test completed successfully!")
        print(f"Results file: {result_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

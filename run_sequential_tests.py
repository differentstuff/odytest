"""
Sequential Test Runner for OdyTest - Model Evaluation Suite
Manages the complete testing workflow across all models
"""

import os
import sys
import glob
import argparse
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (when used as module)
    from .config import get_model_list, get_model_config
    from .test_single_model import test_single_model
    from .results_manager import generate_comparative_report, print_summary
    from .prompt_manager import get_available_variants
except ImportError:
    # Fall back to direct imports (when run as script)
    from config import get_model_list, get_model_config # type: ignore
    from test_single_model import test_single_model
    from results_manager import generate_comparative_report, print_summary
    from prompt_manager import get_available_variants

class SequentialTestRunner:
    """Manages sequential testing of multiple models"""
    
    def __init__(self, prompt_variant: str = "production"):
        self.prompt_variant = prompt_variant
        self.result_files = []
        self.models_tested = []
    
    def run_all_models(self, models: Optional[List[str]] = None) -> bool:
        """
        Run tests for all specified models sequentially
        
        Args:
            models: List of model keys to test, or None for all models
            
        Returns:
            True if all tests completed successfully
        """
        
        if models is None:
            models = get_model_list()

        print(f"\n🚀 OdyTest - Sequential Model Evaluation")
        print("=" * 80)
        print(f"Models to test: {len(models)}")
        print(f"Prompt variant: {self.prompt_variant}")
        print(f"Models: {', '.join(models)}")

        success_count = 0

        for i, model_key in enumerate(models, 1):
            print(f"\n" + "="*80)
            print(f"🔄 TESTING MODEL {i}/{len(models)}: {model_key}")
            print("="*80)

            # Get model info
            try:
                model_config = get_model_config(model_key)
                print(f"📋 Model: {model_config.name}")
                print(f"📝 Description: {model_config.description}")
                print(f"⏱️  Timeout: {model_config.timeout}s")
            except Exception as e:
                print(f"❌ Error getting model config: {e}")
                continue

            # Run test for this model
            print(f"\n🧪 Starting tests for {model_config.name}...")
            result_file = test_single_model(model_key, self.prompt_variant)

            if result_file:
                self.result_files.append(result_file)
                self.models_tested.append(model_key)
                success_count += 1
                print(f"✅ {model_config.name} testing completed successfully")
            else:
                print(f"❌ {model_config.name} testing failed")

            # Prompt user to unload model (except for last model)
            if i < len(models):
                print(f"\n🔧 CLEANUP:")
                exit_code = os.system(f"ollama stop {model_config.name}")
                if exit_code == 0:
                    print(f"   Unloaded '{model_config.name}' from Ollama")
        
        print(f"\n" + "="*80)
        print(f"📊 TESTING SUMMARY")
        print("="*80)
        print(f"Models tested: {success_count}/{len(models)}")
        print(f"Successful tests: {len(self.result_files)}")
        print(f"Failed tests: {len(models) - success_count}")
        
        if self.result_files:
            print(f"Result files generated:")
            for result_file in self.result_files:
                print(f"   📁 {os.path.basename(result_file)}")
        
        return success_count == len(models)
    
    def generate_final_report(self) -> bool:
        """Generate comparative analysis report from all test results"""
        
        if not self.result_files:
            print("❌ No result files available for comparison")
            return False
        
        print(f"\n📊 Generating Comparative Analysis...")
        print(f"Analyzing {len(self.result_files)} result files")
        
        try:
            comparison = generate_comparative_report(self.result_files)
            
            if "error" in comparison:
                print(f"❌ Error generating report: {comparison['error']}")
                return False
            
            # Print summary to console
            print_summary(comparison)
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating comparative report: {e}")
            return False
    
    def run_complete_evaluation(self, models: Optional[List[str]] = None) -> bool:
        """
        Run complete evaluation workflow
        
        Args:
            models: List of model keys to test, or None for all models
            
        Returns:
            True if evaluation completed successfully
        """
        
        print(f"\n🎯 Starting Complete Model Evaluation")
        print(f"Prompt variant: {self.prompt_variant}")
        
        # Run sequential tests
        if not self.run_all_models(models):
            print(f"⚠️  Some tests failed, but continuing with analysis...")
        
        # Generate comparative report
        if self.result_files:
            comparison = self.generate_final_report()
            if comparison:
                print(f"\n🎉 Complete evaluation finished successfully!")
                print(f"📋 Check the comparative analysis report for detailed results")
                return True
        
        print(f"\n❌ Evaluation completed with issues")
        return False

def main():
    """Main entry point for sequential testing"""
    
    parser = argparse.ArgumentParser(
        description="Run sequential model evaluation tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_sequential_tests.py
  python run_sequential_tests.py --prompt multilingual
  python run_sequential_tests.py --models qwen3_4b deepseek_r1
  python run_sequential_tests.py --generate-report-only
        """
    )
    
    parser.add_argument(
        "--prompt",
        choices=list(get_available_variants().keys()),
        default="structured",
        help="Prompt variant to use for all tests (default: production)"
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        choices=get_model_list(),
        help="Specific models to test (default: all models)"
    )
    
    parser.add_argument(
        "--generate-report-only",
        action="store_true",
        help="Generate comparative report from existing result files"
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
    
    # Handle report-only mode
    if args.generate_report_only:
        print("🔍 Searching for existing result files...")
        
        # Find all result files in the results directory
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        if os.path.exists(results_dir):
            result_files = glob.glob(os.path.join(results_dir, "*.json"))
            # Filter out comparative analysis files
            result_files = [f for f in result_files if not os.path.basename(f).startswith("comparative_analysis")]
            
            if result_files:
                print(f"Found {len(result_files)} result files")
                comparison = generate_comparative_report(result_files)
                if comparison and "error" not in comparison:
                    print_summary(comparison)
                    print("✅ Comparative report generated successfully")
                else:
                    print("❌ Failed to generate comparative report")
            else:
                print("❌ No result files found")
        else:
            print("❌ Results directory not found")
        return
    
    # Run sequential tests
    runner = SequentialTestRunner(args.prompt)
    
    try:
        success = runner.run_complete_evaluation(args.models)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

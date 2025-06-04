# OdyTest - Model Evaluation Suite

A comprehensive testing framework for evaluating LLM model performance in semantic parsing tasks for the Roster Assistant project.

## Overview

OdyTest provides a modular, sequential testing approach to fairly compare different LLM models across multiple languages and prompt variants. The name "OdyTest" reflects the journey-like nature of testing multiple models sequentially, like an odyssey through different AI capabilities.

## Features

- **Sequential Model Testing**: Test one model at a time for fair resource allocation
- **Multilingual Support**: Test cases in English, German, French, and Italian
- **Multiple Prompt Variants**: Compare different prompt engineering approaches
- **Comprehensive Metrics**: JSON validity, intent accuracy, entity extraction, timing
- **Automated Reporting**: Generate detailed comparative analysis reports
- **Resource Monitoring**: Track CPU and memory usage during testing
- **Modular Architecture**: Clean separation of concerns for easy maintenance

## Architecture

```
odytest2/
├── config.py              # Model configurations and settings
├── test_cases.py           # Comprehensive multilingual test scenarios
├── prompt_manager.py       # Prompt variants and management
├── model_evaluator.py      # Core testing and evaluation logic
├── results_manager.py      # Result storage and analysis
├── test_single_model.py    # Single model test runner
├── run_sequential_tests.py # Sequential test orchestrator
├── demo.py                 # Demonstration script
├── run.bat                 # Windows batch runner with interactive menu
├── setup.bat               # Environment setup script
└── README.md              # This documentation
```

## Quick Start

### 1. Setup (Windows)

```bash
# Navigate to the odytest2 directory
cd tests/odytest2

# Run setup script to create virtual environment
setup.bat

# Start testing with the runner
run.bat
```

### 2. Easy Usage with Batch Scripts

```bash
# Interactive menu
run.bat

# Quick commands
run.bat demo                    # Show demonstration
run.bat list-models             # List available models
run.bat test gemma3_1b         # Test single model
run.bat sequential             # Test all models
run.bat report                 # Generate comparative report
```

### 3. Direct Python Usage

```bash
# Test with production prompt
python test_single_model.py gemma3_1b

# Test with different prompt variant
python test_single_model.py qwen3_1_7b --prompt multilingual

# List available models and prompts
python test_single_model.py --list-models
python test_single_model.py --list-prompts

# Run sequential tests for all models
python run_sequential_tests.py

# Test specific models with custom prompt
python run_sequential_tests.py --models gemma3_1b qwen3_1_7b --prompt multilingual

# Generate report from existing results
python run_sequential_tests.py --generate-report-only
```

## Supported Models

- **Gemma3-1B**: Simple, lightweight and fast - ideal for quick testing
- **Qwen3-1.7B**: Superior human preference alignment with balanced performance
- **Qwen3-0.6B**: Compact model with superior human preference alignment
- **JOSIEFIED-Qwen3-0.6B**: Modified version of Qwen3 0.6B with enhanced capabilities

## Test Categories

### Emergency Replacement
- Employee unavailability scenarios
- Urgent shift coverage requests
- Multilingual emergency contexts

### Schedule Creation
- Full schedule generation requests
- Optimization preference handling
- Time period specifications

### Information Requests
- Employee availability queries
- Staff capability inquiries
- General information requests

### View Schedule
- Current schedule display requests
- Specific time period views
- Weekend/day-specific queries

### Modifications
- Shift swapping requests
- Employee reassignments
- Schedule adjustments

### Analysis
- Hypothetical scenario evaluation
- Impact analysis requests
- What-if questions

### Edge Cases
- Empty inputs
- Ambiguous requests
- Complex multilingual scenarios

## Prompt Variants

### Production
Current production prompt from semantic parser configuration

### Multilingual
Enhanced with explicit multilingual support and examples

### Concise
Streamlined for faster inference with essential features only

### Structured
Highly organized with clear sections and comprehensive rules

### Chain of Thought
Encourages step-by-step reasoning for complex scenarios

## Evaluation Metrics

### Accuracy Metrics
- **Intent Accuracy**: Correct classification of user intent
- **Entity Extraction**: Accuracy of extracted entities
- **JSON Validity**: Structural correctness of output

### Performance Metrics
- **Inference Time**: Average, median, min/max response times
- **Success Rate**: Percentage of successful API calls
- **Confidence Scores**: Model confidence in predictions

### Language-Specific Analysis
- Per-language accuracy breakdown
- Multilingual capability assessment
- Language-specific recommendations

### Difficulty Analysis
- Performance across different complexity levels
- Edge case handling capabilities
- Robustness evaluation

## Usage Examples

### Testing Workflow

1. **Load Model in Ollama**
   ```bash
   ollama pull gemma3:1b
   ```

2. **Run Single Model Test**
   ```bash
   python test_single_model.py gemma3_1b
   ```

3. **Unload Model and Load Next**
   ```bash
   ollama rm gemma3:1b
   ollama pull qwen3:1.7b
   ```

4. **Continue Testing**
   ```bash
   python test_single_model.py qwen3_1_7b
   ```

5. **Generate Comparative Report**
   ```bash
   python run_sequential_tests.py --generate-report-only
   ```

### Programmatic Usage

```python
from test_single_model import test_single_model
from run_sequential_tests import SequentialTestRunner
from test_cases import get_test_summary
from demo import demo_test_suite_overview

# Print package information
demo_test_suite_overview()

# Get test suite summary
summary = get_test_summary()
print(f"Total test cases: {summary['total_cases']}")

# Test single model
result_file = test_single_model("gemma3_1b", "multilingual")

# Run sequential tests
runner = SequentialTestRunner("production")
success = runner.run_complete_evaluation(["gemma3_1b", "qwen3_1_7b"])
```

## Output Files

### Individual Model Results
```
results/gemma3_1b_production_20250603_143000.json
```

Contains:
- Test metadata (model, prompt, timestamp)
- Summary statistics
- Detailed results for each test case
- Performance metrics

### Comparative Analysis
```
results/comparative_analysis_20250603_143000.json
```

Contains:
- Model rankings by different criteria
- Performance comparison matrix
- Language-specific analysis
- Deployment recommendations

## Configuration

### Model Configuration
```python
MODEL_CONFIGS = {
    "gemma3_1b": ModelConfig(
        name="gemma3:1b",
        temperature=0.1,
        top_p=0.95,
        timeout=10,
        max_retries=3,
        description="gemma3 1b - Simple, lightweight and fast"
    )
}
```

### Test Configuration
```python
TEST_CONFIG = {
    "max_retries": 2,
    "retry_delay": 1.0,
    "save_raw_outputs": True,
    "validate_checksums": True,
    "monitor_resources": True
}
```

## Best Practices

### Fair Testing
1. Test one model at a time to ensure fair resource allocation
2. Use identical test cases across all models
3. Monitor system resources during testing
4. Validate model availability before testing

### Result Analysis
1. Compare models using multiple metrics, not just accuracy
2. Consider language-specific performance differences
3. Evaluate speed vs. accuracy trade-offs
4. Review edge case handling capabilities

### Production Deployment
1. Use comparative analysis for model selection
2. Consider specific language requirements
3. Balance accuracy and inference speed
4. Test with production-like workloads

## Troubleshooting

### Common Issues

**Model Not Available**
- Ensure Ollama is running
- Verify model is loaded: `ollama list`
- Check model name spelling

**Import Errors**
- Ensure you're in the project root directory
- Check Python path configuration
- Verify all dependencies are installed

**Memory Issues**
- Test one model at a time
- Unload models between tests
- Monitor system resources

**JSON Validation Failures**
- Check prompt formatting
- Verify model output structure
- Review validation criteria

### Dependencies

```bash
pip install requests psutil ollama httpx
```

## Contributing

When adding new test cases:
1. Follow the existing TestCase structure
2. Include expected entities and intents
3. Add appropriate difficulty and category labels
4. Test across multiple languages when applicable

When adding new models:
1. Update MODEL_CONFIGS in config.py
2. Test with existing test suite
3. Verify timeout and parameter settings
4. Document model-specific considerations

## License

This testing framework is part of the Roster Assistant project and follows the same licensing terms.

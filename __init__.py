"""
OdyTest - Model Evaluation Suite for Roster Assistant
A comprehensive testing framework for evaluating LLM model performance
"""

__version__ = "1.0.0"
__author__ = "Roster Assistant Team"
__description__ = "Sequential model evaluation suite for semantic parsing performance"

# Import main components for easy access
from .config import MODEL_CONFIGS, get_model_config, get_model_list
from .test_cases import get_test_cases, get_test_summary
from .model_evaluator import create_evaluator, TestResult
from .results_manager import save_results, generate_comparative_report, print_summary
from .prompt_manager import get_prompt, get_available_variants
from .test_single_model import test_single_model
from .run_sequential_tests import SequentialTestRunner

__all__ = [
    # Configuration
    'MODEL_CONFIGS',
    'get_model_config',
    'get_model_list',
    
    # Test cases
    'get_test_cases',
    'get_test_summary',
    
    # Model evaluation
    'create_evaluator',
    'TestResult',
    'test_single_model',
    
    # Results management
    'save_results',
    'generate_comparative_report',
    'print_summary',
    
    # Prompt management
    'get_prompt',
    'get_available_variants',
    
    # Test runners
    'SequentialTestRunner',
]

# Package metadata
PACKAGE_INFO = {
    "name": "odytest",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "features": [
        "Sequential model testing for fair comparison",
        "Multilingual test cases (English, German, French, Italian)",
        "Multiple prompt variants for optimization",
        "Comprehensive performance metrics",
        "Automated report generation",
        "JSON validation and accuracy scoring",
        "Resource usage monitoring"
    ],
    "supported_models": [
        "Qwen3-4B",
        "DeepSeek-R1-0528-Qwen3-8B", 
        "llama-3.3-8b-instruct"
    ],
    "test_categories": [
        "emergency_replacement",
        "schedule_creation",
        "information_requests",
        "view_schedule",
        "modifications",
        "analysis",
        "edge_cases"
    ]
}

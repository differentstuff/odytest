"""
Configuration module for OdyTest - Model Evaluation Suite
Contains model configurations and test parameters
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a single model"""
    name: str
    temperature: float
    top_p: float
    timeout: int
    max_retries: int
    description: str

# Model configurations for testing
MODEL_CONFIGS = {
    "gemma3_1b": ModelConfig(
        name="gemma3:1b",
        temperature=0.1,
        top_p=0.95,
        timeout=10,
        max_retries=3,
        description="gemma3 1b - Simple, lightweight and fast"
    ),
    "qwen3_1_7b": ModelConfig(
        name="qwen3:1.7b",
        temperature=0.1,
        top_p=0.95,
        timeout=10,
        max_retries=3,
        description="qwen3 1.7b - Superior human preference alignment"
    ),
    "qwen3_0_6b": ModelConfig(
        name="qwen3:0.6b",
        temperature=0.1,
        top_p=0.95,
        timeout=10,
        max_retries=3,
        description="qwen3 0.6b - Superior human preference alignment"
    ),
    "qwen3_0_6b_mod": ModelConfig(
        name="goekdenizguelmez/JOSIEFIED-Qwen3:0.6b",
        temperature=0.1,
        top_p=0.95,
        timeout=10,
        max_retries=3,
        description="qwen3 0.6b JOSIEFIED - Modified version of Qwen3 0.6b"
    )
}

# Test execution settings
TEST_CONFIG = {
    "max_retries": 2,
    "retry_delay": 1.0,
    "save_raw_outputs": True,
    "validate_checksums": True,
    "monitor_resources": True
}

# Output settings
OUTPUT_CONFIG = {
    "results_dir": "results",
    "timestamp_format": "%Y%m%d_%H%M%S",
    "json_indent": 2,
    "save_individual_results": True,
    "generate_summary": True
}

# Evaluation criteria
EVALUATION_CRITERIA = {
    "required_fields": ["intent", "entities", "confidence"],
    "valid_intents": [
        "view_schedule", "emergency_replacement", "create_schedule",
        "modify_schedule", "analyze_scenario", "information", "unknown"
    ],
    "confidence_range": (0.0, 1.0),
    "entity_fields": [
        "employee_name", "shift_day", "shift_time", "shift_name",
        "optimization_preference", "time_period", "urgency"
    ]
}

def get_model_list() -> List[str]:
    """Get list of model keys for sequential testing"""
    return list(MODEL_CONFIGS.keys())

def get_model_config(model_key: str) -> ModelConfig:
    """Get configuration for specific model"""
    if model_key not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model: {model_key}")
    return MODEL_CONFIGS[model_key]

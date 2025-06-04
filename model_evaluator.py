"""
Model Evaluator for OdyTest - Model Evaluation Suite
Handles model testing, JSON validation, and performance metrics
"""

import json
import time
import re
import psutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

try:
    # Try relative imports first (when used as module)
    from .config import ModelConfig, EVALUATION_CRITERIA, TEST_CONFIG
    from .test_cases import TestCase
    from .prompt_manager import get_prompt
    from .test_ollama_library import OllamaClient, OllamaConfig, OllamaError, JSONParseError
except ImportError:
    # Fall back to direct imports (when run as script)
    from config import ModelConfig, EVALUATION_CRITERIA, TEST_CONFIG # type: ignore
    from test_cases import TestCase
    from prompt_manager import get_prompt
    from test_ollama_library import OllamaClient, OllamaConfig, OllamaError, JSONParseError

@dataclass
class TestResult:
    """Result of a single test case execution"""
    model_name: str
    prompt_variant: str
    test_case_id: int
    input_query: str
    expected_intent: str
    expected_entities: Dict[str, Any]
    language: str
    difficulty: str
    category: str
    
    # Execution results
    success: bool
    inference_time: float
    raw_output: str
    
    # JSON validation
    json_validity: bool
    parsed_json: Optional[Dict[str, Any]]
    validation_error: Optional[str]
    
    # Accuracy metrics
    intent_match: bool
    intent_accuracy_type: str  # "exact", "better", "worse", "different"
    entity_accuracy: Dict[str, Any]
    confidence_score: Optional[float]
    
    # System metrics
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    
    # Error information
    error_message: Optional[str]

class ModelEvaluator:
    """Evaluates model performance on test cases"""
    
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        # Create OllamaClient configuration
        ollama_config = OllamaConfig(
            model=model_config.name,
            temperature=model_config.temperature,
            top_p=model_config.top_p,
            timeout=model_config.timeout,
            max_retries=model_config.max_retries
        )
        self.ollama_client = OllamaClient(ollama_config)
    
    def test_model_availability(self) -> bool:
        """Test if model is available via Ollama"""
        try:
            # Use a simple test prompt
            self.ollama_client.generate("Test", stream=False)
            return True
        except Exception:
            return False
    
    def query_model(self, prompt: str) -> Tuple[bool, Optional[str], float, Optional[str]]:
        """
        Query model and return success, response, timing, and error
        
        Returns:
            (success, response, inference_time, error_message)
        """
        start_time = time.time()
        
        try:
            response = self.ollama_client.generate(prompt, stream=False)
            inference_time = time.time() - start_time
            return True, response, inference_time, None
            
        except OllamaError as e:
            inference_time = time.time() - start_time
            return False, None, inference_time, str(e)
            
        except Exception as e:
            inference_time = time.time() - start_time
            return False, None, inference_time, f"Unexpected error: {str(e)}"
    
    def extract_and_validate_json(self, llm_output: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Extract and validate JSON from LLM output"""
        
        # Find JSON in the response
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if not json_match:
            return False, None, "No JSON found in output"
        
        try:
            parsed_json = json.loads(json_match.group())
            
            # Validate required fields
            missing_fields = [
                field for field in EVALUATION_CRITERIA["required_fields"] 
                if field not in parsed_json
            ]
            
            if missing_fields:
                return False, parsed_json, f"Missing required fields: {missing_fields}"
            
            # Validate intent
            if parsed_json.get('intent') not in EVALUATION_CRITERIA["valid_intents"]:
                return False, parsed_json, f"Invalid intent: {parsed_json.get('intent')}"
            
            # Validate confidence range
            confidence = parsed_json.get('confidence')
            if not isinstance(confidence, (int, float)):
                return False, parsed_json, "Confidence must be a number"
            
            min_conf, max_conf = EVALUATION_CRITERIA["confidence_range"]
            if not (min_conf <= confidence <= max_conf):
                return False, parsed_json, f"Confidence {confidence} outside valid range {min_conf}-{max_conf}"
            
            # Validate entities structure
            if not isinstance(parsed_json.get('entities'), dict):
                return False, parsed_json, "Entities must be a dictionary"
            
            return True, parsed_json, "Valid JSON"
            
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {e}"
    
    def evaluate_intent_accuracy(self, expected: str, actual: str) -> Tuple[bool, str]:
        """
        Evaluate intent classification accuracy
        
        Returns:
            (is_match, accuracy_type)
        """
        if expected == actual:
            return True, "exact"
        elif expected == "unknown" and actual != "unknown":
            return False, "better"  # Model found intent when we expected unknown
        elif expected != "unknown" and actual == "unknown":
            return False, "worse"   # Model couldn't classify when we expected specific intent
        else:
            return False, "different"  # Different but both are specific intents
    
    def evaluate_entity_extraction(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate entity extraction accuracy"""
        
        # Filter out null values from actual entities for comparison
        actual_filtered = {k: v for k, v in actual.items() if v is not None}
        
        results = {
            "total_expected": len(expected),
            "total_extracted": len(actual_filtered),
            "correct_extractions": 0,
            "missing_entities": [],
            "extra_entities": [],
            "incorrect_values": [],
            "accuracy_score": 0.0
        }
        
        # Check expected entities
        for key, expected_value in expected.items():
            if key in actual_filtered:
                if actual_filtered[key] == expected_value:
                    results["correct_extractions"] += 1
                else:
                    results["incorrect_values"].append({
                        "entity": key,
                        "expected": expected_value,
                        "actual": actual_filtered[key]
                    })
            else:
                results["missing_entities"].append(key)
        
        # Check for extra entities
        for key in actual_filtered:
            if key not in expected:
                results["extra_entities"].append(key)
        
        # Calculate accuracy score
        if results["total_expected"] > 0:
            results["accuracy_score"] = results["correct_extractions"] / results["total_expected"]
        else:
            results["accuracy_score"] = 1.0 if results["total_extracted"] == 0 else 0.0
        
        return results
    
    def execute_test_case(self, test_case: TestCase, prompt_variant: str, test_id: int) -> TestResult:
        """Execute a single test case"""
        
        # Get system metrics before test
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent
        
        # Generate prompt
        prompt = get_prompt(prompt_variant, test_case.input)
        
        # Query model
        success, response, inference_time, error_message = self.query_model(prompt)
        
        # Get system metrics after test
        cpu_after = psutil.cpu_percent()
        memory_after = psutil.virtual_memory().percent
        
        # Initialize result
        result = TestResult(
            model_name=self.model_config.name,
            prompt_variant=prompt_variant,
            test_case_id=test_id,
            input_query=test_case.input,
            expected_intent=test_case.expected_intent,
            expected_entities=test_case.expected_entities,
            language=test_case.language,
            difficulty=test_case.difficulty,
            category=test_case.category,
            success=success,
            inference_time=inference_time,
            raw_output=response or "",
            json_validity=False,
            parsed_json=None,
            validation_error=None,
            intent_match=False,
            intent_accuracy_type="unknown",
            entity_accuracy={},
            confidence_score=None,
            cpu_usage=(cpu_after - cpu_before) if cpu_after > cpu_before else 0.0,
            memory_usage=(memory_after - memory_before) if memory_after > memory_before else 0.0,
            error_message=error_message
        )
        
        if not success or response is None:
            return result
        
        # Validate JSON
        json_valid, parsed_json, validation_error = self.extract_and_validate_json(response)
        result.json_validity = json_valid
        result.parsed_json = parsed_json
        result.validation_error = validation_error if not json_valid else None
        
        if not json_valid or parsed_json is None:
            return result
        
        # Evaluate intent accuracy
        intent_match, accuracy_type = self.evaluate_intent_accuracy(
            test_case.expected_intent,
            parsed_json.get('intent', 'unknown')
        )
        result.intent_match = intent_match
        result.intent_accuracy_type = accuracy_type
        
        # Evaluate entity extraction
        result.entity_accuracy = self.evaluate_entity_extraction(
            test_case.expected_entities,
            parsed_json.get('entities', {})
        )
        
        # Extract confidence score
        result.confidence_score = parsed_json.get('confidence', 0.0)
        
        return result
    
    def execute_test_suite(self, test_cases: List[TestCase], prompt_variant: str = "production") -> List[TestResult]:
        """Execute full test suite for this model"""
        
        print(f"✅ Model '{self.model_config.name}' validated successfully")
        print("=" * 60)
        
        # Check model availability
        if not self.test_model_availability():
            print(f"❌ Model {self.model_config.name} not available")
            return []
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"📝 Test {i+1}/{len(test_cases)}: {test_case.input[:50]}...")
            print(f"   Language: {test_case.language}")
            print(f"   Difficulty: {test_case.difficulty}")
            
            result = self.execute_test_case(test_case, prompt_variant, i)
            results.append(result)
            
            # Print immediate feedback
            if result.success and result.json_validity and result.parsed_json:
                response_status = "✅ Response: ok"
                intent_status = "✅" if result.intent_match else "❌"
                entity_score = result.entity_accuracy.get('accuracy_score', 0.0)
                print(f"   {response_status}")
                print(f"   {intent_status} Intent: {result.parsed_json.get('intent')} (Expected: {test_case.expected_intent})")
                print(f"   Entity Accuracy: {entity_score:.1%}, Confidence: {result.confidence_score:.2f}")
                print(f"   Time: {result.inference_time:.2f}s")
            elif result.success:
                print(f"   ❌ Response: JSON Invalid - {result.validation_error}")
                print(f"   Time: {result.inference_time:.2f}s")
            else:
                print(f"   ❌ Response: Failed - {result.error_message}")
                print(f"   Time: {result.inference_time:.2f}s")
        
        return results
    
    def generate_summary_stats(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate summary statistics for test results"""
        
        if not results:
            return {"error": "No results to analyze"}
        
        total_tests = len(results)
        successful_tests = [r for r in results if r.success]
        valid_json_tests = [r for r in results if r.json_validity]
        intent_matches = [r for r in results if r.intent_match]
        
        # Basic metrics
        stats = {
            "total_tests": total_tests,
            "success_rate": len(successful_tests) / total_tests,
            "json_validity_rate": len(valid_json_tests) / total_tests,
            "intent_accuracy_rate": len(intent_matches) / total_tests,
            "model_name": self.model_config.name,
            "model_description": self.model_config.description
        }
        
        if successful_tests:
            # Timing statistics
            inference_times = [r.inference_time for r in successful_tests]
            stats["timing"] = {
                "avg_inference_time": statistics.mean(inference_times),
                "median_inference_time": statistics.median(inference_times),
                "min_inference_time": min(inference_times),
                "max_inference_time": max(inference_times)
            }
            
            # Confidence statistics
            if valid_json_tests:
                confidence_scores = [r.confidence_score for r in valid_json_tests if r.confidence_score is not None]
                if confidence_scores:
                    stats["confidence"] = {
                        "avg_confidence": statistics.mean(confidence_scores),
                        "median_confidence": statistics.median(confidence_scores),
                        "min_confidence": min(confidence_scores),
                        "max_confidence": max(confidence_scores)
                    }
        
        # Language breakdown
        languages = {}
        for lang in set(r.language for r in results):
            lang_results = [r for r in results if r.language == lang]
            lang_matches = [r for r in lang_results if r.intent_match]
            languages[lang] = {
                "total": len(lang_results),
                "accuracy": len(lang_matches) / len(lang_results) if lang_results else 0.0
            }
        stats["by_language"] = languages
        
        # Difficulty breakdown
        difficulties = {}
        for diff in set(r.difficulty for r in results):
            diff_results = [r for r in results if r.difficulty == diff]
            diff_matches = [r for r in diff_results if r.intent_match]
            difficulties[diff] = {
                "total": len(diff_results),
                "accuracy": len(diff_matches) / len(diff_results) if diff_results else 0.0
            }
        stats["by_difficulty"] = difficulties
        
        # Category breakdown
        categories = {}
        for cat in set(r.category for r in results):
            cat_results = [r for r in results if r.category == cat]
            cat_matches = [r for r in cat_results if r.intent_match]
            categories[cat] = {
                "total": len(cat_results),
                "accuracy": len(cat_matches) / len(cat_results) if cat_results else 0.0
            }
        stats["by_category"] = categories
        
        return stats

def create_evaluator(model_config: ModelConfig) -> ModelEvaluator:
    """Factory function to create model evaluator"""
    return ModelEvaluator(model_config)

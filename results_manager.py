"""
Results Manager for OdyTest - Model Evaluation Suite
Handles result storage, analysis, and report generation
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import statistics

try:
    # Try relative imports first (when used as module)
    from .config import OUTPUT_CONFIG
    from .model_evaluator import TestResult
except ImportError:
    # Fall back to direct imports (when run as script)
    from config import OUTPUT_CONFIG # type: ignore
    from model_evaluator import TestResult

class ResultsManager:
    """Manages test results storage and analysis"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.results_dir = os.path.join(base_dir, OUTPUT_CONFIG["results_dir"])
        self._ensure_results_directory()
    
    def _ensure_results_directory(self):
        """Create results directory if it doesn't exist"""
        os.makedirs(self.results_dir, exist_ok=True)
    
    def save_model_results(self, model_name: str, prompt_variant: str, results: List[TestResult], 
                          summary_stats: Dict[str, Any]) -> str:
        """Save results for a single model test run"""
        
        timestamp = time.strftime(OUTPUT_CONFIG["timestamp_format"])
        # Replace colons and other invalid characters for Windows filenames
        safe_model_name = model_name.replace(":", "_").replace("/", "_").replace("\\", "_")
        filename = f"{safe_model_name}_{prompt_variant}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        # Convert results to serializable format
        serializable_results = [asdict(result) for result in results]
        
        output_data = {
            "metadata": {
                "model_name": model_name,
                "prompt_variant": prompt_variant,
                "timestamp": timestamp,
                "total_test_cases": len(results),
                "test_duration": self._calculate_total_duration(results)
            },
            "summary_stats": summary_stats,
            "detailed_results": serializable_results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=OUTPUT_CONFIG["json_indent"], ensure_ascii=False)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath
    
    def _calculate_total_duration(self, results: List[TestResult]) -> float:
        """Calculate total test duration"""
        return sum(result.inference_time for result in results if result.success)
    
    def load_model_results(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load results from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading results from {filepath}: {e}")
            return None
    
    def generate_comparative_report(self, result_files: List[str]) -> Dict[str, Any]:
        """Generate comparative analysis across multiple model results"""
        
        print("\n📊 Generating Comparative Analysis Report")
        print("=" * 60)
        
        all_results = {}
        
        # Load all result files
        for filepath in result_files:
            data = self.load_model_results(filepath)
            if data:
                model_name = data["metadata"]["model_name"]
                prompt_variant = data["metadata"]["prompt_variant"]
                key = f"{model_name}_{prompt_variant}"
                all_results[key] = data
        
        if not all_results:
            return {"error": "No valid result files found"}
        
        # Generate comparative analysis
        comparison = self._analyze_model_performance(all_results)
        
        # Save comparative report
        timestamp = time.strftime(OUTPUT_CONFIG["timestamp_format"])
        report_filename = f"comparative_analysis_{timestamp}.json"
        report_filepath = os.path.join(self.results_dir, report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=OUTPUT_CONFIG["json_indent"], ensure_ascii=False)
        
        print(f"📋 Comparative report saved to: {report_filepath}")
        return comparison
    
    def _analyze_model_performance(self, all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance across all models"""
        
        analysis = {
            "summary": {
                "total_models_tested": len(all_results),
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_cases_per_model": None
            },
            "model_rankings": {},
            "performance_comparison": {},
            "language_analysis": {},
            "difficulty_analysis": {},
            "recommendations": []
        }
        
        # Extract performance metrics for each model
        model_metrics = {}
        
        for key, data in all_results.items():
            stats = data["summary_stats"]
            model_name = data["metadata"]["model_name"]
            prompt_variant = data["metadata"]["prompt_variant"]
            
            model_metrics[key] = {
                "model_name": model_name,
                "prompt_variant": prompt_variant,
                "intent_accuracy": stats.get("intent_accuracy_rate", 0.0),
                "json_validity": stats.get("json_validity_rate", 0.0),
                "avg_inference_time": stats.get("timing", {}).get("avg_inference_time", float('inf')),
                "avg_confidence": stats.get("confidence", {}).get("avg_confidence", 0.0),
                "success_rate": stats.get("success_rate", 0.0),
                "total_tests": stats.get("total_tests", 0),
                "by_language": stats.get("by_language", {}),
                "by_difficulty": stats.get("by_difficulty", {}),
                "by_category": stats.get("by_category", {})
            }
        
        analysis["summary"]["test_cases_per_model"] = list(set(m["total_tests"] for m in model_metrics.values()))
        
        # Generate rankings
        analysis["model_rankings"] = self._generate_rankings(model_metrics)
        
        # Performance comparison matrix
        analysis["performance_comparison"] = self._create_performance_matrix(model_metrics)
        
        # Language-specific analysis
        analysis["language_analysis"] = self._analyze_language_performance(model_metrics)
        
        # Difficulty analysis
        analysis["difficulty_analysis"] = self._analyze_difficulty_performance(model_metrics)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(model_metrics, analysis)
        
        return analysis
    
    def _generate_rankings(self, model_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate model rankings by different criteria"""
        
        rankings = {}
        
        # Overall accuracy ranking (intent accuracy + json validity)
        overall_scores = []
        for key, metrics in model_metrics.items():
            overall_score = (metrics["intent_accuracy"] * 0.7 + metrics["json_validity"] * 0.3)
            overall_scores.append({
                "model": key,
                "model_name": metrics["model_name"],
                "prompt_variant": metrics["prompt_variant"],
                "score": overall_score,
                "intent_accuracy": metrics["intent_accuracy"],
                "json_validity": metrics["json_validity"]
            })
        
        rankings["overall_accuracy"] = sorted(overall_scores, key=lambda x: x["score"], reverse=True)
        
        # Speed ranking
        speed_scores = []
        for key, metrics in model_metrics.items():
            if metrics["avg_inference_time"] != float('inf'):
                speed_scores.append({
                    "model": key,
                    "model_name": metrics["model_name"],
                    "prompt_variant": metrics["prompt_variant"],
                    "avg_inference_time": metrics["avg_inference_time"]
                })
        
        rankings["speed"] = sorted(speed_scores, key=lambda x: x["avg_inference_time"])
        
        # Confidence ranking
        confidence_scores = []
        for key, metrics in model_metrics.items():
            if metrics["avg_confidence"] > 0:
                confidence_scores.append({
                    "model": key,
                    "model_name": metrics["model_name"],
                    "prompt_variant": metrics["prompt_variant"],
                    "avg_confidence": metrics["avg_confidence"]
                })
        
        rankings["confidence"] = sorted(confidence_scores, key=lambda x: x["avg_confidence"], reverse=True)
        
        return rankings
    
    def _create_performance_matrix(self, model_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Create performance comparison matrix"""
        
        matrix = {}
        
        for key, metrics in model_metrics.items():
            matrix[key] = {
                "intent_accuracy": metrics["intent_accuracy"],
                "json_validity": metrics["json_validity"],
                "avg_inference_time": metrics["avg_inference_time"] if metrics["avg_inference_time"] != float('inf') else None,
                "avg_confidence": metrics["avg_confidence"],
                "success_rate": metrics["success_rate"]
            }
        
        return matrix
    
    def _analyze_language_performance(self, model_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by language"""
        
        languages = set()
        for metrics in model_metrics.values():
            languages.update(metrics["by_language"].keys())
        
        language_analysis = {}
        
        for lang in languages:
            lang_scores = []
            for key, metrics in model_metrics.items():
                if lang in metrics["by_language"]:
                    lang_scores.append({
                        "model": key,
                        "accuracy": metrics["by_language"][lang]["accuracy"]
                    })
            
            if lang_scores:
                language_analysis[lang] = {
                    "best_model": max(lang_scores, key=lambda x: x["accuracy"])["model"],
                    "avg_accuracy": statistics.mean([s["accuracy"] for s in lang_scores]),
                    "model_scores": {s["model"]: s["accuracy"] for s in lang_scores}
                }
        
        return language_analysis
    
    def _analyze_difficulty_performance(self, model_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by difficulty level"""
        
        difficulties = set()
        for metrics in model_metrics.values():
            difficulties.update(metrics["by_difficulty"].keys())
        
        difficulty_analysis = {}
        
        for diff in difficulties:
            diff_scores = []
            for key, metrics in model_metrics.items():
                if diff in metrics["by_difficulty"]:
                    diff_scores.append({
                        "model": key,
                        "accuracy": metrics["by_difficulty"][diff]["accuracy"]
                    })
            
            if diff_scores:
                difficulty_analysis[diff] = {
                    "best_model": max(diff_scores, key=lambda x: x["accuracy"])["model"],
                    "avg_accuracy": statistics.mean([s["accuracy"] for s in diff_scores]),
                    "model_scores": {s["model"]: s["accuracy"] for s in diff_scores}
                }
        
        return difficulty_analysis
    
    def _generate_recommendations(self, model_metrics: Dict[str, Dict[str, Any]], 
                                analysis: Dict[str, Any]) -> List[str]:
        """Generate deployment recommendations"""
        
        recommendations = []
        
        # Best overall model
        if analysis["model_rankings"]["overall_accuracy"]:
            best_overall = analysis["model_rankings"]["overall_accuracy"][0]
            recommendations.append(
                f"🏆 Best Overall Performance: {best_overall['model_name']} with {best_overall['prompt_variant']} prompt "
                f"({best_overall['score']:.1%} combined score)"
            )
        
        # Fastest model
        if analysis["model_rankings"]["speed"]:
            fastest = analysis["model_rankings"]["speed"][0]
            recommendations.append(
                f"⚡ Fastest Inference: {fastest['model_name']} with {fastest['prompt_variant']} prompt "
                f"({fastest['avg_inference_time']:.2f}s average)"
            )
        
        # Language-specific recommendations
        for lang, lang_data in analysis["language_analysis"].items():
            best_model = lang_data["best_model"]
            model_name = model_metrics[best_model]["model_name"]
            prompt_variant = model_metrics[best_model]["prompt_variant"]
            accuracy = lang_data["model_scores"][best_model]
            recommendations.append(
                f"🌍 Best for {lang}: {model_name} with {prompt_variant} prompt ({accuracy:.1%} accuracy)"
            )
        
        # Production deployment recommendation
        if model_metrics:
            # Find model with best balance of accuracy and speed
            balanced_scores = []
            for key, metrics in model_metrics.items():
                if metrics["avg_inference_time"] != float('inf'):
                    # Normalize speed (lower is better) and combine with accuracy
                    max_time = max(m["avg_inference_time"] for m in model_metrics.values() 
                                 if m["avg_inference_time"] != float('inf'))
                    speed_score = 1 - (metrics["avg_inference_time"] / max_time)
                    balanced_score = (metrics["intent_accuracy"] * 0.6 + speed_score * 0.4)
                    balanced_scores.append((key, balanced_score, metrics))
            
            if balanced_scores:
                best_balanced = max(balanced_scores, key=lambda x: x[1])
                key, score, metrics = best_balanced
                recommendations.append(
                    f"🎯 Production Recommendation: {metrics['model_name']} with {metrics['prompt_variant']} prompt "
                    f"(balanced score: {score:.1%}, accuracy: {metrics['intent_accuracy']:.1%}, "
                    f"speed: {metrics['avg_inference_time']:.2f}s)"
                )
        
        return recommendations
    
    def print_summary_report(self, comparison: Dict[str, Any]):
        """Print a formatted summary report to console"""
        
        print("\n" + "="*80)
        print("🏆 ODYTEST MODEL EVALUATION SUMMARY REPORT")
        print("="*80)
        
        # Summary
        summary = comparison["summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Models Tested: {summary['total_models_tested']}")
        print(f"   Test Cases per Model: {summary['test_cases_per_model']}")
        print(f"   Analysis Date: {summary['analysis_timestamp']}")
        
        # Rankings
        rankings = comparison["model_rankings"]
        
        if rankings.get("overall_accuracy"):
            print(f"\n🏆 Overall Performance Ranking:")
            for i, model in enumerate(rankings["overall_accuracy"][:3], 1):
                print(f"   {i}. {model['model_name']} ({model['prompt_variant']}) - {model['score']:.1%}")
        
        if rankings.get("speed"):
            print(f"\n⚡ Speed Ranking:")
            for i, model in enumerate(rankings["speed"][:3], 1):
                print(f"   {i}. {model['model_name']} ({model['prompt_variant']}) - {model['avg_inference_time']:.2f}s")
        
        # Language performance
        lang_analysis = comparison["language_analysis"]
        if lang_analysis:
            print(f"\n🌍 Language-Specific Best Performers:")
            for lang, data in lang_analysis.items():
                best_model = data["best_model"]
                accuracy = data["model_scores"][best_model]
                print(f"   {lang}: {best_model} ({accuracy:.1%})")
        
        # Recommendations
        recommendations = comparison["recommendations"]
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   {rec}")
        
        print("\n" + "="*80)

# Global instance for easy access
results_manager = ResultsManager()

def save_results(model_name: str, prompt_variant: str, results: List[TestResult], 
                summary_stats: Dict[str, Any]) -> str:
    """Save model test results"""
    return results_manager.save_model_results(model_name, prompt_variant, results, summary_stats)

def generate_comparative_report(result_files: List[str]) -> Dict[str, Any]:
    """Generate comparative analysis report"""
    return results_manager.generate_comparative_report(result_files)

def print_summary(comparison: Dict[str, Any]):
    """Print summary report to console"""
    results_manager.print_summary_report(comparison)

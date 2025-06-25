"""
Logging utilities for experiment tracking and result analysis.
"""
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class ExperimentResult:
    """Single experiment result."""
    timestamp: str
    framework: str
    task_id: str
    task_type: str
    run_number: int
    success: bool
    tokens_used: int
    execution_time: float
    memory_usage: float
    reasoning_steps: int
    final_answer: str
    intermediate_steps: List[str]
    validation_score: float
    validation_passed: bool
    validation_issues: List[str]
    error_message: Optional[str] = None


class ExperimentLogger:
    """Handles logging and storage of experiment results."""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("experiment_logger")
        self.logger.setLevel(logging.INFO)
        
        # Create formatters and handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        log_file = self.results_dir / f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Results storage
        self.results: List[ExperimentResult] = []
        
    def log_result(self, result: ExperimentResult):
        """Log a single experiment result."""
        self.results.append(result)
        
        self.logger.info(
            f"Framework: {result.framework}, Task: {result.task_id}, "
            f"Run: {result.run_number}, Success: {result.success}, "
            f"Score: {result.validation_score:.1f}, "
            f"Time: {result.execution_time:.2f}s, "
            f"Tokens: {result.tokens_used}"
        )
        
        if not result.success:
            self.logger.error(f"Task failed: {result.error_message}")
        
        if not result.validation_passed:
            self.logger.warning(f"Validation issues: {result.validation_issues}")
    
    def save_results_json(self, filename: Optional[str] = None):
        """Save all results to JSON file."""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        
        results_data = [asdict(result) for result in self.results]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filepath}")
        return filepath
    
    def save_results_csv(self, filename: Optional[str] = None):
        """Save results summary to CSV file."""
        if filename is None:
            filename = f"results_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.results_dir / filename
        
        # Convert to DataFrame and save
        df = pd.DataFrame([asdict(result) for result in self.results])
        
        # Drop complex columns for CSV
        columns_to_drop = ['intermediate_steps', 'validation_issues']
        df_simple = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        df_simple.to_csv(filepath, index=False)
        
        self.logger.info(f"CSV summary saved to {filepath}")
        return filepath
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics from all results."""
        if not self.results:
            return {}
        
        df = pd.DataFrame([asdict(result) for result in self.results])
        
        summary = {
            "total_experiments": len(self.results),
            "success_rate": df['success'].mean(),
            "avg_validation_score": df['validation_score'].mean(),
            "avg_execution_time": df['execution_time'].mean(),
            "avg_tokens_used": df['tokens_used'].mean(),
            "avg_reasoning_steps": df['reasoning_steps'].mean(),
        }
        
        # Framework-specific stats
        framework_stats = {}
        for framework in df['framework'].unique():
            framework_df = df[df['framework'] == framework]
            framework_stats[framework] = {
                "success_rate": framework_df['success'].mean(),
                "avg_validation_score": framework_df['validation_score'].mean(),
                "avg_execution_time": framework_df['execution_time'].mean(),
                "avg_tokens_used": framework_df['tokens_used'].mean(),
                "avg_reasoning_steps": framework_df['reasoning_steps'].mean(),
            }
        
        summary["framework_stats"] = framework_stats
        
        # Task type stats
        task_type_stats = {}
        for task_type in df['task_type'].unique():
            task_df = df[df['task_type'] == task_type]
            task_type_stats[task_type] = {
                "success_rate": task_df['success'].mean(),
                "avg_validation_score": task_df['validation_score'].mean(),
                "avg_execution_time": task_df['execution_time'].mean(),
                "avg_tokens_used": task_df['tokens_used'].mean(),
            }
        
        summary["task_type_stats"] = task_type_stats
        
        return summary
    
    def save_summary_report(self, filename: Optional[str] = None):
        """Save a comprehensive summary report."""
        if filename is None:
            filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        
        summary = self.generate_summary_stats()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Summary report saved to {filepath}")
        return filepath
    
    def print_summary(self):
        """Print summary statistics to console."""
        summary = self.generate_summary_stats()
        
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY")
        print("="*60)
        
        print(f"Total Experiments: {summary.get('total_experiments', 0)}")
        print(f"Overall Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"Average Validation Score: {summary.get('avg_validation_score', 0):.1f}")
        print(f"Average Execution Time: {summary.get('avg_execution_time', 0):.2f}s")
        print(f"Average Tokens Used: {summary.get('avg_tokens_used', 0):.0f}")
        print(f"Average Reasoning Steps: {summary.get('avg_reasoning_steps', 0):.1f}")
        
        print("\nFRAMEWORK COMPARISON:")
        print("-"*40)
        for framework, stats in summary.get('framework_stats', {}).items():
            print(f"{framework.upper()}:")
            print(f"  Success Rate: {stats['success_rate']:.1%}")
            print(f"  Avg Score: {stats['avg_validation_score']:.1f}")
            print(f"  Avg Time: {stats['avg_execution_time']:.2f}s")
            print(f"  Avg Tokens: {stats['avg_tokens_used']:.0f}")
        
        print("\nTASK TYPE PERFORMANCE:")
        print("-"*40)
        for task_type, stats in summary.get('task_type_stats', {}).items():
            print(f"{task_type.replace('_', ' ').title()}:")
            print(f"  Success Rate: {stats['success_rate']:.1%}")
            print(f"  Avg Score: {stats['avg_validation_score']:.1f}")
            print(f"  Avg Time: {stats['avg_execution_time']:.2f}s")
        
        print("="*60)

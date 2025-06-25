"""
Main experiment runner for comparing reasoning frameworks.
"""
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import AgentFactory
from tasks import TaskGenerator, TaskValidator
from utils import ExperimentLogger, ExperimentResult, LLMManager


class ExperimentRunner:
    """Orchestrates the comparison experiment across all frameworks and tasks."""
    
    def __init__(self, 
                 model_name: str = None,
                 temperature: float = None,
                 runs_per_task: int = None,
                 results_dir: str = "results",
                 framework_cooldown: float = None,
                 run_cooldown: float = None):
        
        load_dotenv()
        
        # Configuration
        self.model_name = model_name or os.getenv('DEFAULT_MODEL', 'gemini-2.0-flash-exp')
        self.temperature = temperature or float(os.getenv('TEMPERATURE', 0.3))
        self.runs_per_task = runs_per_task or int(os.getenv('RUNS_PER_TASK', 3))
        
        # Cooldown parameters for rate limiting
        self.framework_cooldown = framework_cooldown or float(os.getenv('FRAMEWORK_COOLDOWN', 0))
        self.run_cooldown = run_cooldown or float(os.getenv('RUN_COOLDOWN', 0))
        
        # Initialize components
        self.llm_manager = LLMManager()
        self.logger = ExperimentLogger(results_dir)
        self.task_generator = TaskGenerator()
        self.task_validator = TaskValidator()
        
        # Get tasks and frameworks
        self.all_tasks = self.task_generator.get_all_tasks()
        self.frameworks = AgentFactory.get_available_frameworks()
        
        print(f"Initialized experiment with:")
        print(f"  Model: {self.model_name}")
        print(f"  Temperature: {self.temperature}")
        print(f"  Runs per task: {self.runs_per_task}")
        print(f"  Framework cooldown: {self.framework_cooldown}s")
        print(f"  Run cooldown: {self.run_cooldown}s")
        print(f"  Frameworks: {self.frameworks}")
        print(f"  Task types: {list(self.all_tasks.keys())}")
        print(f"  Total tasks: {sum(len(tasks) for tasks in self.all_tasks.values())}")
        
        # Suggest cooldowns if none are set and using a rate-limited model
        if self.framework_cooldown == 0 and self.run_cooldown == 0:
            if any(term in self.model_name.lower() for term in ['gemini', 'free', 'flash']):
                self._suggest_cooldown_settings()
    
    def run_single_experiment(self, framework: str, task, run_number: int) -> ExperimentResult:
        """Run a single experiment: one framework on one task."""
        timestamp = datetime.now().isoformat()
        
        try:
            # Create LLM and agent
            llm = self.llm_manager.create_llm(
                self.model_name,
                temperature=self.temperature
            )
            agent = AgentFactory.create_agent(framework, llm)
            
            # Execute task
            metrics = agent.execute_task(task.prompt, task.task_type)
            
            # Validate output
            validation_passed, validation_issues, validation_score = \
                self.task_validator.validate_task_output(task, metrics.final_answer)
            
            # Create result
            result = ExperimentResult(
                timestamp=timestamp,
                framework=framework,
                task_id=task.id,
                task_type=task.task_type,
                run_number=run_number,
                success=metrics.success,
                tokens_used=metrics.tokens_used,
                execution_time=metrics.execution_time,
                memory_usage=metrics.memory_usage,
                reasoning_steps=metrics.reasoning_steps,
                final_answer=metrics.final_answer,
                intermediate_steps=metrics.intermediate_steps,
                validation_score=validation_score,
                validation_passed=validation_passed,
                validation_issues=validation_issues,
                error_message=metrics.error_message
            )
            
        except Exception as e:
            # Handle any unexpected errors
            error_str = str(e)
            
            # Check if this is a rate limit error and suggest cooldown
            suggested_cooldown = self._handle_rate_limit_error(error_str)
            if suggested_cooldown and (self.framework_cooldown == 0 or self.run_cooldown == 0):
                print(f"\n⚠️  Rate limit detected! Consider using:")
                print(f"   --framework-cooldown {suggested_cooldown} --run-cooldown {suggested_cooldown/6:.0f}")
                print(f"   Or use: --rate-limited (sets 60s/10s cooldowns)")
            
            result = ExperimentResult(
                timestamp=timestamp,
                framework=framework,
                task_id=task.id,
                task_type=task.task_type,
                run_number=run_number,
                success=False,
                tokens_used=0,
                execution_time=0.0,
                memory_usage=0.0,
                reasoning_steps=0,
                final_answer="",
                intermediate_steps=[],
                validation_score=0.0,
                validation_passed=False,
                validation_issues=[f"Experiment error: {error_str}"],
                error_message=error_str
            )
        
        self.logger.log_result(result)
        return result
    
    def run_framework_comparison(self, 
                                frameworks: Optional[List[str]] = None,
                                task_types: Optional[List[str]] = None,
                                specific_tasks: Optional[List[str]] = None) -> List[ExperimentResult]:
        """Run comparison across specified frameworks and tasks."""
        
        frameworks = frameworks or self.frameworks
        task_types = task_types or list(self.all_tasks.keys())
        
        results = []
        total_experiments = 0
        
        # Calculate total experiments
        for task_type in task_types:
            tasks = self.all_tasks[task_type]
            if specific_tasks:
                tasks = [t for t in tasks if t.id in specific_tasks]
            total_experiments += len(tasks) * len(frameworks) * self.runs_per_task
        
        print(f"\nStarting {total_experiments} experiments...")
        print("="*60)
        
        experiment_count = 0
        
        for task_type in task_types:
            tasks = self.all_tasks[task_type]
            if specific_tasks:
                tasks = [t for t in tasks if t.id in specific_tasks]
            
            print(f"\nProcessing {task_type.replace('_', ' ').title()} tasks...")
            
            for task in tasks:
                print(f"\n  Task: {task.title} ({task.id})")
                
                for framework_idx, framework in enumerate(frameworks):
                    print(f"    Framework: {framework.upper()}")
                    
                    # Add cooldown between frameworks (except for the first one)
                    if framework_idx > 0 and self.framework_cooldown > 0:
                        print(f"      ⏱️  Framework cooldown: {self.framework_cooldown}s")
                        time.sleep(self.framework_cooldown)
                    
                    for run in range(1, self.runs_per_task + 1):
                        experiment_count += 1
                        print(f"      Run {run}/{self.runs_per_task} [{experiment_count}/{total_experiments}]", end=" ")
                        
                        result = self.run_single_experiment(framework, task, run)
                        results.append(result)
                        
                        # Quick status
                        status = "✓" if result.success else "✗"
                        score = f"{result.validation_score:.0f}" if result.success else "0"
                        print(f"- {status} Score: {score}")
                        
                        # Add cooldown between runs (except for the last one)
                        if run < self.runs_per_task and self.run_cooldown > 0:
                            print(f"        ⏱️  Run cooldown: {self.run_cooldown}s")
                            time.sleep(self.run_cooldown)
        
        print("\n" + "="*60)
        print("All experiments completed!")
        
        return results
    
    def run_full_experiment(self) -> List[ExperimentResult]:
        """Run the complete experiment across all frameworks and tasks."""
        return self.run_framework_comparison()
    
    def save_results(self, results: List[ExperimentResult]):
        """Save experiment results to files."""
        print("\nSaving results...")
        
        json_file = self.logger.save_results_json()
        csv_file = self.logger.save_results_csv()
        summary_file = self.logger.save_summary_report()
        
        print(f"  JSON results: {json_file}")
        print(f"  CSV summary: {csv_file}")
        print(f"  Summary report: {summary_file}")
        
        # Print summary to console
        self.logger.print_summary()
    
    def run_quick_test(self) -> List[ExperimentResult]:
        """Run a quick test with just one task per type and one run."""
        print("Running quick test (1 task per type, 1 run each)...")
        
        # Select first task from each type
        quick_tasks = []
        for task_type, tasks in self.all_tasks.items():
            if tasks:
                quick_tasks.append(tasks[0].id)
        
        # Temporarily set runs to 1
        original_runs = self.runs_per_task
        self.runs_per_task = 1
        
        results = self.run_framework_comparison(specific_tasks=quick_tasks)
        
        # Restore original runs
        self.runs_per_task = original_runs
        
        return results

    def _handle_rate_limit_error(self, error_message: str) -> Optional[float]:
        """
        Analyze rate limit error and suggest cooldown time.
        Returns suggested cooldown in seconds or None if not a rate limit error.
        """
        if not error_message:
            return None
            
        error_lower = error_message.lower()
        
        # Check for common rate limit indicators
        rate_limit_indicators = [
            "quota", "rate limit", "too many requests", "429", 
            "exceeded", "per minute", "per hour"
        ]
        
        if any(indicator in error_lower for indicator in rate_limit_indicators):
            # Extract retry delay if available
            if "retry_delay" in error_message and "seconds:" in error_message:
                try:
                    import re
                    delay_match = re.search(r'seconds:\s*(\d+)', error_message)
                    if delay_match:
                        return float(delay_match.group(1)) + 5  # Add 5 seconds buffer
                except:
                    pass
            
            # Default suggestions based on API
            if "gemini" in error_lower or "google" in error_lower:
                return 60.0  # Google free tier: 10 requests per minute
            elif "openai" in error_lower:
                return 20.0  # OpenAI rate limits vary
            elif "mistral" in error_lower:
                return 30.0  # Mistral rate limits
            else:
                return 60.0  # Conservative default
        
        return None
    
    def _suggest_cooldown_settings(self):
        """Suggest cooldown settings based on the model being used."""
        suggestions = {
            'gemini-2.0-flash-exp': {'framework': 60, 'run': 10, 'reason': 'Free tier: 10 requests/minute'},
            'gemini-1.5-pro': {'framework': 30, 'run': 5, 'reason': 'Paid tier with moderate limits'},
            'gpt-3.5-turbo': {'framework': 20, 'run': 3, 'reason': 'OpenAI tier 1 limits'},
            'gpt-4': {'framework': 60, 'run': 10, 'reason': 'GPT-4 stricter limits'},
            'mistral-small': {'framework': 30, 'run': 5, 'reason': 'Mistral API limits'}
        }
        
        model_suggestion = suggestions.get(self.model_name)
        if model_suggestion:
            print(f"\n💡 Suggested cooldown settings for {self.model_name}:")
            print(f"   --framework-cooldown {model_suggestion['framework']} --run-cooldown {model_suggestion['run']}")
            print(f"   Reason: {model_suggestion['reason']}")
        else:
            print(f"\n💡 For rate limiting, try: --framework-cooldown 60 --run-cooldown 10")

def main():
    """Main entry point for the experiment."""
    print("LLM Reasoning Framework Comparison Experiment")
    print("=" * 50)
    
    # Check for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run LLM reasoning framework comparison')
    parser.add_argument('--model', type=str, help='Model to use (default from .env)')
    parser.add_argument('--temperature', type=float, help='Temperature setting (default from .env)')
    parser.add_argument('--runs', type=int, help='Runs per task (default from .env)')
    parser.add_argument('--framework-cooldown', type=float, help='Cooldown between frameworks in seconds (default from .env)')
    parser.add_argument('--run-cooldown', type=float, help='Cooldown between runs in seconds (default from .env)')
    parser.add_argument('--quick', action='store_true', help='Run quick test instead of full experiment')
    parser.add_argument('--frameworks', nargs='+', help='Specific frameworks to test')
    parser.add_argument('--task-types', nargs='+', help='Specific task types to test')
    parser.add_argument('--rate-limited', action='store_true', help='Use rate-limited settings (60s framework cooldown)')
    
    args = parser.parse_args()
    
    # Handle rate-limited preset
    framework_cooldown = args.framework_cooldown
    run_cooldown = args.run_cooldown
    
    if args.rate_limited:
        framework_cooldown = framework_cooldown or 60.0  # 1 minute between frameworks
        run_cooldown = run_cooldown or 10.0  # 10 seconds between runs
        print("🐌 Rate-limited mode enabled (60s framework cooldown, 10s run cooldown)")
    
    # Initialize runner
    runner = ExperimentRunner(
        model_name=args.model,
        temperature=args.temperature, 
        runs_per_task=args.runs,
        framework_cooldown=framework_cooldown,
        run_cooldown=run_cooldown
    )
    
    try:
        # Run experiment
        if args.quick:
            results = runner.run_quick_test()
        elif args.frameworks or args.task_types:
            results = runner.run_framework_comparison(
                frameworks=args.frameworks,
                task_types=args.task_types
            )
        else:
            results = runner.run_full_experiment()
        
        # Save results
        runner.save_results(results)
        
        print(f"\nExperiment completed successfully!")
        print(f"Total results: {len(results)}")
        
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user.")
        if runner.logger.results:
            print("Saving partial results...")
            runner.save_results(runner.logger.results)
    except Exception as e:
        print(f"\nExperiment failed with error: {e}")
        if runner.logger.results:
            print("Saving partial results...")
            runner.save_results(runner.logger.results)
        raise


if __name__ == "__main__":
    main()

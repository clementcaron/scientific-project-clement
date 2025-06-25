"""
Simplified LLM Reasoning Framework Comparison Experiment.
"""
import os
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import AgentFactory
from tasks import TaskGenerator, TaskValidator
from utils import ExperimentLogger, ExperimentResult, LLMManager


class ExperimentRunner:
    """Simple experiment runner with rate limiting enabled by default."""
    
    def __init__(self, 
                 model_name: str = None,
                 temperature: float = None,
                 runs_per_task: int = None,
                 results_dir: str = "results",
                 enable_rate_limiting: bool = True):
        
        load_dotenv()
        
        # Configuration
        self.model_name = model_name or os.getenv('DEFAULT_MODEL')
        self.temperature = temperature or float(os.getenv('TEMPERATURE', 0.3))
        self.runs_per_task = runs_per_task or int(os.getenv('RUNS_PER_TASK', 3))
        
        # Rate limiting (ON by default)
        if enable_rate_limiting:
            self.framework_cooldown = 60.0  # 1 minute between frameworks
            self.run_cooldown = 10.0        # 10 seconds between runs
        else:
            self.framework_cooldown = 0.0
            self.run_cooldown = 0.0
        
        # Initialize components
        self.llm_manager = LLMManager()
        self.logger = ExperimentLogger(results_dir)
        self.task_generator = TaskGenerator()
        self.task_validator = TaskValidator()
        
        # Get tasks and frameworks
        self.all_tasks = self.task_generator.get_all_tasks()
        self.frameworks = AgentFactory.get_available_frameworks()
        
        print(f"Experiment Configuration:")
        print(f"  Model: {self.model_name}")
        print(f"  Runs per task: {self.runs_per_task}")
        print(f"  Rate limiting: {'ON' if enable_rate_limiting else 'OFF'}")
        if enable_rate_limiting:
            print(f"    Framework cooldown: {self.framework_cooldown}s")
            print(f"    Run cooldown: {self.run_cooldown}s")
        print(f"  Available frameworks: {len(self.frameworks)}")
        print(f"  Available tasks: {sum(len(tasks) for tasks in self.all_tasks.values())}")
        
        # Note: Total experiments will be shown when the actual experiment starts
    
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
            
            # Save individual response
            self.save_individual_response(result)
            
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
            # Only count if there are actual tasks to run
            if tasks:
                total_experiments += len(tasks) * len(frameworks) * self.runs_per_task
        
        print(f"\nStarting {total_experiments} experiments...")
        print("="*60)
        
        experiment_count = 0
        
        for task_type in task_types:
            tasks = self.all_tasks[task_type]
            if specific_tasks:
                tasks = [t for t in tasks if t.id in specific_tasks]
            
            # Skip task types with no matching tasks
            if not tasks:
                continue
                
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
                        print(f"      Run {run}/{self.runs_per_task} [{experiment_count}/{total_experiments}]")
                        
                        result = self.run_single_experiment(framework, task, run)
                        results.append(result)
                        
                        # Display results in detail
                        status = "✓" if result.success else "✗"
                        score = f"{result.validation_score:.0f}" if result.success else "0"
                        
                        print(f"        Status: {status} | Score: {score}/100 | Time: {result.execution_time:.1f}s | Tokens: {result.tokens_used}")
                        
                        # Show preview of LLM answer
                        if result.final_answer:
                            from tasks.validators import TaskValidator
                            preview = TaskValidator.format_output_preview(result.final_answer, 150)
                            print(f"        Answer: {preview}")
                        
                        # Show validation issues if any
                        if result.validation_issues:
                            print(f"        Issues: {', '.join(result.validation_issues[:2])}")
                        
                        print()  # Add spacing
                        
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
        validation_summary = self.save_validation_summary(results)
        
        print(f"  JSON results: {json_file}")
        print(f"  CSV summary: {csv_file}")
        print(f"  Summary report: {summary_file}")
        print(f"  Individual responses: results/responses/ ({len(results)} files)")
        print(f"  Validation summary: {validation_summary}")
        
        # Print summary to console
        self.logger.print_summary()
    
    def run_quick_test(self) -> List[ExperimentResult]:
        """Run a quick test with one task from each type (3 frameworks × 3 tasks = 9 experiments)."""
        print("Running quick test (3 frameworks × 3 task types = 9 experiments total)")
        print("Testing one task from each type:")
        print("  • code_001 (Conway's Game of Life)")
        print("  • itin_001 (European City Tour)")
        print("  • proc_001 (Software Deployment Process)")
        
        # Select one task from each type for comprehensive testing
        quick_tasks = ["code_001", "itin_001", "proc_001"]
        
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
            else:
                return 60.0  # Conservative default
        
        return None
    
    def save_individual_response(self, result: ExperimentResult) -> str:
        """Save individual LLM response to a separate file."""
        # Create responses directory
        responses_dir = Path("results/responses")
        responses_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp, framework, task, and run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{result.framework}_{result.task_id}_run{result.run_number}.txt"
        filepath = responses_dir / filename
        
        # Prepare content
        content = f"""LLM Response Analysis
====================
Timestamp: {result.timestamp}
Framework: {result.framework}
Task ID: {result.task_id}
Task Type: {result.task_type}
Run Number: {result.run_number}
Model: {self.model_name}
Success: {result.success}
Execution Time: {result.execution_time:.2f}s
Tokens Used: {result.tokens_used}
Validation Score: {result.validation_score}/100
Validation Passed: {result.validation_passed}

Validation Issues:
{chr(10).join(f"- {issue}" for issue in result.validation_issues) if result.validation_issues else "None"}

Reasoning Steps:
{"=" * 50}
{chr(10).join(f"Step {i+1}: {step}" for i, step in enumerate(result.intermediate_steps))}

Final Answer:
{"=" * 50}
{result.final_answer}

Error Message (if any):
{"=" * 50}
{result.error_message or "None"}
"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)

    def save_validation_summary(self, results: List[ExperimentResult]) -> str:
        """Save a comprehensive validation summary across all experiments."""
        responses_dir = Path("results/responses")
        responses_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = responses_dir / f"validation_summary_{timestamp}.txt"
        
        # Group results by framework
        frameworks = {}
        for result in results:
            if result.framework not in frameworks:
                frameworks[result.framework] = []
            frameworks[result.framework].append(result)
        
        content = f"""Validation Summary Report
=========================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Experiments: {len(results)}
Model Used: {self.model_name}

Overall Statistics:
------------------
Success Rate: {sum(1 for r in results if r.success) / len(results) * 100:.1f}%
Average Execution Time: {sum(r.execution_time for r in results) / len(results):.2f}s
Average Tokens Used: {sum(r.tokens_used for r in results) / len(results):.0f}
Average Validation Score: {sum(r.validation_score for r in results) / len(results):.1f}/100
Validation Pass Rate: {sum(1 for r in results if r.validation_passed) / len(results) * 100:.1f}%

Framework Comparison:
====================
"""
        
        for framework, framework_results in frameworks.items():
            avg_score = sum(r.validation_score for r in framework_results) / len(framework_results)
            avg_time = sum(r.execution_time for r in framework_results) / len(framework_results)
            avg_tokens = sum(r.tokens_used for r in framework_results) / len(framework_results)
            pass_rate = sum(1 for r in framework_results if r.validation_passed) / len(framework_results) * 100
            
            content += f"""
{framework.upper()} Framework:
{"-" * (len(framework) + 11)}
• Experiments: {len(framework_results)}
• Average Score: {avg_score:.1f}/100
• Pass Rate: {pass_rate:.1f}%
• Average Time: {avg_time:.2f}s
• Average Tokens: {avg_tokens:.0f}
• Common Issues: {", ".join(set(issue for r in framework_results for issue in r.validation_issues)) or "None"}
"""
        
        content += f"""

Detailed Results:
================
"""
        
        for result in results:
            content += f"""
{result.framework.upper()} - {result.task_id} - Run {result.run_number}:
• Score: {result.validation_score}/100 | Pass: {result.validation_passed} | Time: {result.execution_time:.2f}s
• Issues: {", ".join(result.validation_issues) if result.validation_issues else "None"}
• Answer Length: {len(result.final_answer)} characters
• Steps: {result.reasoning_steps}
"""
        
        # Write to file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(summary_file)

def main():
    """Simplified main entry point."""
    print("🧠 LLM Reasoning Framework Comparison")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(
        description='Compare ReAct, CoT, and ToT frameworks across 3 task types',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_experiment.py --quick          # Quick test (9 experiments: all frameworks × 3 task types)
  python run_experiment.py                  # Full experiment (9 runs with 3x repetition) 
  python run_experiment.py --no-limit       # Disable rate limiting
  python run_experiment.py --runs 1         # Single run per task
        """
    )
    
    parser.add_argument('--model', type=str, help='LLM model to use')
    parser.add_argument('--temperature', type=float, help='Temperature (0.0-1.0)')
    parser.add_argument('--runs', type=int, help='Runs per framework per task')
    parser.add_argument('--quick', action='store_true', help='Quick test (9 experiments: all frameworks on all 3 task types)')
    parser.add_argument('--no-limit', action='store_true', help='Disable rate limiting')
    parser.add_argument('--frameworks', nargs='+', choices=['react', 'cot', 'tot'], help='Specific frameworks')
    
    args = parser.parse_args()
    
    # Handle quick mode
    runs = 1 if args.quick else (args.runs or 3)
    
    # Rate limiting (ON by default, disabled with --no-limit)
    enable_rate_limiting = not args.no_limit
    
    if enable_rate_limiting:
        print("🐌 Rate limiting: ON (60s between frameworks, 10s between runs)")
        print("   Use --no-limit to disable")
    else:
        print("⚡ Rate limiting: OFF")
    
    # Initialize runner
    runner = ExperimentRunner(
        model_name=args.model,
        temperature=args.temperature,
        runs_per_task=runs,
        enable_rate_limiting=enable_rate_limiting
    )
    
    try:
        # Run experiment
        if args.frameworks:
            print(f"\n🎯 Testing specific frameworks: {args.frameworks}")
            results = runner.run_framework_comparison(frameworks=args.frameworks)
        elif args.quick:
            print(f"\n🚀 Running quick test...")
            results = runner.run_quick_test()
        else:
            print(f"\n🚀 Running full experiment...")
            results = runner.run_framework_comparison()
        
        # Save and summarize results
        runner.save_results(results)
        print(f"\n✅ Experiment completed: {len(results)} results")
        print(f"📁 Results saved to: results/")
        print(f"📊 Open experiment.ipynb for detailed analysis")
        
    except KeyboardInterrupt:
        print("\n⏹️  Experiment interrupted by user")
        if hasattr(runner, 'logger') and runner.logger.results:
            runner.save_results(runner.logger.results)
            print("💾 Partial results saved")
    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        if hasattr(runner, 'logger') and runner.logger.results:
            runner.save_results(runner.logger.results)
            print("💾 Partial results saved")
        sys.exit(1)


if __name__ == "__main__":
    main()

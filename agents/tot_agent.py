"""
Tree-of-Thoughts (ToT) Agent Implementation.
Explores multiple reasoning paths and selects the best approach.
"""
import re
from typing import List, Dict, Any, Tuple
from langchain.llms.base import LLM
from .base_agent import BaseAgent, ExecutionMetrics


class ToTAgent(BaseAgent):
    """Tree-of-Thoughts agent that explores multiple reasoning paths."""
    
    def __init__(self, llm: LLM, temperature: float = 0.3, max_tokens: int = 2048, num_branches: int = 3):
        super().__init__(llm, temperature, max_tokens)
        self.num_branches = num_branches
    
    def get_framework_prompt(self, task_prompt: str, task_type: str) -> str:
        """Generate ToT-specific prompt with multiple path exploration."""
        base_prompt = f"""You are solving a {task_type} task using Tree-of-Thoughts reasoning. Explore multiple approaches and select the best one.

Task: {task_prompt}

Follow this structure:

APPROACH GENERATION:
Generate {self.num_branches} different approaches to solve this problem:

Approach 1: [Describe first potential method]
Approach 2: [Describe second potential method]  
Approach 3: [Describe third potential method]

APPROACH EVALUATION:
Evaluate each approach:

Approach 1 Assessment: [Pros, cons, feasibility - Rate 1-10]
Approach 2 Assessment: [Pros, cons, feasibility - Rate 1-10]
Approach 3 Assessment: [Pros, cons, feasibility - Rate 1-10]

BEST APPROACH SELECTION:
Selected Approach: [Choose the highest-rated approach and explain why]

DETAILED EXECUTION:
Now implement the selected approach step by step:
Step 1: [First implementation step]
Step 2: [Second implementation step]
...
Step N: [Final step]

Final Solution: [Complete solution using the best approach]

Task-specific considerations:
- Code Generation: Consider different algorithms, data structures, complexity trade-offs
- Itinerary Planning: Explore different route options, transportation modes, optimization criteria
- Procedure Structuring: Try different organizational frameworks, sequencing approaches

Begin exploration:
"""
        return base_prompt
    
    def execute_task(self, task_prompt: str, task_type: str) -> ExecutionMetrics:
        """Execute task using Tree-of-Thoughts framework."""
        full_prompt = self.get_framework_prompt(task_prompt, task_type)
        
        def _run_tot():
            response = self.llm.invoke(full_prompt)
            return response
        
        result, exec_time, memory_usage, success, error = self._measure_execution(_run_tot)
        
        if not success:
            return ExecutionMetrics(
                tokens_used=0,
                execution_time=exec_time,
                memory_usage=memory_usage,
                reasoning_steps=0,
                final_answer="",
                intermediate_steps=[],
                success=False,
                error_message=error
            )
        
        # Parse ToT response
        reasoning_steps = self._extract_reasoning_steps(result)
        final_answer = self._extract_final_answer(result)
        tokens_used = self._count_tokens(full_prompt + str(result))
        
        return ExecutionMetrics(
            tokens_used=tokens_used,
            execution_time=exec_time,
            memory_usage=memory_usage,
            reasoning_steps=len(reasoning_steps),
            final_answer=final_answer,
            intermediate_steps=reasoning_steps,
            success=True
        )
    
    def _extract_reasoning_steps(self, response: str) -> List[str]:
        """Extract the different phases of ToT reasoning."""
        steps = []
        
        # Extract approaches
        approach_pattern = r"Approach\s*(\d+):\s*(.*?)(?=\nApproach\s*\d+:|APPROACH EVALUATION:|$)"
        approaches = re.findall(approach_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for approach_num, approach_content in approaches:
            steps.append(f"Generated Approach {approach_num}: {approach_content.strip()}")
        
        # Extract evaluations
        eval_pattern = r"Approach\s*(\d+)\s*Assessment:\s*(.*?)(?=\nApproach\s*\d+\s*Assessment:|BEST APPROACH SELECTION:|$)"
        evaluations = re.findall(eval_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for eval_num, eval_content in evaluations:
            steps.append(f"Evaluated Approach {eval_num}: {eval_content.strip()}")
        
        # Extract selected approach
        selection_pattern = r"Selected Approach:\s*(.*?)(?=\nDETAILED EXECUTION:|$)"
        selection_match = re.search(selection_pattern, response, re.DOTALL | re.IGNORECASE)
        if selection_match:
            steps.append(f"Selected Best Approach: {selection_match.group(1).strip()}")
        
        # Extract execution steps
        exec_step_pattern = r"Step\s*(\d+):\s*(.*?)(?=\nStep\s*\d+:|Final Solution:|$)"
        exec_steps = re.findall(exec_step_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for step_num, step_content in exec_steps:
            steps.append(f"Execution Step {step_num}: {step_content.strip()}")
        
        return steps
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract the final solution from ToT response."""
        # Look for "Final Solution:" pattern
        final_pattern = r"Final Solution:\s*(.*?)(?=\n\w+:|$)"
        match = re.search(final_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Alternative patterns
        alt_patterns = [
            r"Final Answer:\s*(.*?)(?=\n\w+:|$)",
            r"Solution:\s*(.*?)(?=\n\w+:|$)",
            r"Complete solution:\s*(.*?)(?=\n\w+:|$)"
        ]
        
        for pattern in alt_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit final answer, look for the last substantial content
        lines = response.strip().split('\n')
        
        # Try to find code blocks or substantial content at the end
        result_lines = []
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith(('step', 'approach')):
                break
            result_lines.insert(0, line)
        
        return '\n'.join(result_lines) if result_lines else (lines[-1] if lines else "")
    
    def _extract_approach_scores(self, response: str) -> Dict[int, float]:
        """Extract scores for each approach (if provided)."""
        scores = {}
        
        # Look for ratings in evaluations
        rating_pattern = r"Approach\s*(\d+)\s*Assessment:.*?(\d+(?:\.\d+)?)/10"
        matches = re.findall(rating_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for approach_num, score in matches:
            try:
                scores[int(approach_num)] = float(score)
            except ValueError:
                continue
        
        return scores

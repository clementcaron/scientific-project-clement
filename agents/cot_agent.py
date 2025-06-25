"""
Chain-of-Thought (CoT) Agent Implementation.
Uses step-by-step reasoning in a linear fashion.
"""
import re
from typing import List, Dict, Any
from langchain.llms.base import LLM
from .base_agent import BaseAgent, ExecutionMetrics


class CoTAgent(BaseAgent):
    """Chain-of-Thought agent that uses linear step-by-step reasoning."""
    
    def __init__(self, llm: LLM, temperature: float = 0.3, max_tokens: int = 2048):
        super().__init__(llm, temperature, max_tokens)
    
    def get_framework_prompt(self, task_prompt: str, task_type: str) -> str:
        """Generate CoT-specific prompt with step-by-step reasoning structure."""
        base_prompt = f"""You are solving a {task_type} task. Use Chain-of-Thought reasoning: break down the problem into clear, logical steps.

Task: {task_prompt}

Think through this step by step:

Step 1: [Understand the problem and identify key requirements]
Step 2: [Break down the problem into smaller components]
Step 3: [Plan your approach or algorithm]
Step 4: [Implement/work through the first part]
Step 5: [Continue with subsequent parts]
...
Step N: [Complete the solution and verify]

Final Solution: [Your complete answer]

Guidelines for each task type:
- Code Generation: Analyze requirements → Design algorithm → Implement incrementally → Test logic
- Itinerary Planning: Parse constraints → Research options → Calculate costs/times → Optimize route
- Procedure Structuring: Identify core objectives → Break into logical steps → Sequence properly → Add details

Let's work through this systematically:
"""
        return base_prompt
    
    def execute_task(self, task_prompt: str, task_type: str) -> ExecutionMetrics:
        """Execute task using Chain-of-Thought framework."""
        full_prompt = self.get_framework_prompt(task_prompt, task_type)
        
        def _run_cot():
            response = self.llm.invoke(full_prompt)
            return response
        
        result, exec_time, memory_usage, success, error = self._measure_execution(_run_cot)
        
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
        
        # Parse CoT response
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
        """Extract numbered steps from CoT response."""
        steps = []
        
        # Find all numbered steps
        step_pattern = r"Step\s*(\d+):\s*(.*?)(?=\nStep\s*\d+:|Final Solution:|$)"
        matches = re.findall(step_pattern, response, re.DOTALL | re.IGNORECASE)
        
        for step_num, step_content in matches:
            steps.append(f"Step {step_num}: {step_content.strip()}")
        
        # If no numbered steps found, try to split by logical breaks
        if not steps:
            lines = response.split('\n')
            current_step = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_step:
                        steps.append(' '.join(current_step))
                        current_step = []
                elif line.lower().startswith(('step', 'first', 'second', 'third', 'next', 'then', 'finally')):
                    if current_step:
                        steps.append(' '.join(current_step))
                    current_step = [line]
                else:
                    current_step.append(line)
            
            if current_step:
                steps.append(' '.join(current_step))
        
        return steps
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract the final solution from CoT response."""
        # Look for "Final Solution:" or similar patterns
        final_patterns = [
            r"Final Solution:\s*(.*?)(?:\n|$)",
            r"Final Answer:\s*(.*?)(?:\n|$)",
            r"Solution:\s*(.*?)(?:\n|$)",
            r"Answer:\s*(.*?)(?:\n|$)"
        ]
        
        for pattern in final_patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no explicit final answer, return the last meaningful section
        lines = response.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not line.lower().startswith('step'):
                return line
        
        return lines[-1] if lines else ""

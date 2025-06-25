"""
ReAct (Reasoning + Acting) Agent Implementation.
Alternates between reasoning about the problem and taking actions.
"""
import re
from typing import List, Dict, Any
from langchain.llms.base import LLM
from .base_agent import BaseAgent, ExecutionMetrics


class ReActAgent(BaseAgent):
    """ReAct agent that alternates between reasoning and acting."""
    
    def __init__(self, llm: LLM, temperature: float = 0.3, max_tokens: int = 2048, max_iterations: int = 6):
        super().__init__(llm, temperature, max_tokens)
        self.max_iterations = max_iterations
    
    def get_framework_prompt(self, task_prompt: str, task_type: str) -> str:
        """Generate ReAct-specific prompt with reasoning and action structure."""
        base_prompt = f"""You are solving a {task_type} task. Use the ReAct framework: alternate between Thought and Action steps.

Task: {task_prompt}

Follow this exact format:
Thought: [Your reasoning about what to do next]
Action: [The specific action you're taking]
Observation: [What you learned from the action]

Continue this Thought-Action-Observation cycle until you reach a final answer.
When you have the complete solution, end with:
Final Answer: [Your complete solution]

Important guidelines:
- For code generation: Think through the algorithm step by step, then implement incrementally
- For itinerary planning: Consider constraints, calculate distances/times, optimize step by step  
- For procedure structuring: Analyze the vague instructions, identify key steps, organize logically

Begin:
"""
        return base_prompt
    
    def execute_task(self, task_prompt: str, task_type: str) -> ExecutionMetrics:
        """Execute task using ReAct framework."""
        full_prompt = self.get_framework_prompt(task_prompt, task_type)
        
        def _run_react():
            response = self.llm.invoke(full_prompt)
            return response
        
        result, exec_time, memory_usage, success, error = self._measure_execution(_run_react)
        
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
        
        # Parse ReAct response
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
        """Extract Thought-Action-Observation cycles from ReAct response."""
        steps = []
        
        # Find all Thought-Action-Observation patterns
        thought_pattern = r"Thought:\s*(.*?)(?=\nAction:|$)"
        action_pattern = r"Action:\s*(.*?)(?=\nObservation:|$)"
        observation_pattern = r"Observation:\s*(.*?)(?=\nThought:|Final Answer:|$)"
        
        thoughts = re.findall(thought_pattern, response, re.DOTALL | re.IGNORECASE)
        actions = re.findall(action_pattern, response, re.DOTALL | re.IGNORECASE)
        observations = re.findall(observation_pattern, response, re.DOTALL | re.IGNORECASE)
        
        # Combine into reasoning steps
        max_len = max(len(thoughts), len(actions), len(observations))
        for i in range(max_len):
            step_parts = []
            if i < len(thoughts):
                step_parts.append(f"Thought: {thoughts[i].strip()}")
            if i < len(actions):
                step_parts.append(f"Action: {actions[i].strip()}")
            if i < len(observations):
                step_parts.append(f"Observation: {observations[i].strip()}")
            
            if step_parts:
                steps.append(" | ".join(step_parts))
        
        return steps
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract the final answer from ReAct response."""
        final_answer_pattern = r"Final Answer:\s*(.*?)(?=\n\w+:|$)"
        match = re.search(final_answer_pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # If no "Final Answer" found, look for the last substantial content
        lines = response.strip().split('\n')
        
        # Try to find code blocks or substantial content at the end
        result_lines = []
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith(('thought:', 'action:', 'observation:')):
                break
            result_lines.insert(0, line)
        
        return '\n'.join(result_lines) if result_lines else (lines[-1] if lines else "")

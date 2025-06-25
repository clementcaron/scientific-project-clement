"""
Base agent class for implementing different reasoning frameworks.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import psutil
import os
from langchain.llms.base import LLM
from langchain.schema import BaseMessage


@dataclass
class ExecutionMetrics:
    """Metrics collected during agent execution."""
    tokens_used: int
    execution_time: float
    memory_usage: float
    reasoning_steps: int
    final_answer: str
    intermediate_steps: List[str]
    success: bool
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all reasoning framework agents."""
    
    def __init__(self, llm: LLM, temperature: float = 0.3, max_tokens: int = 2048):
        self.llm = llm
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.framework_name = self.__class__.__name__
        
    @abstractmethod
    def execute_task(self, task_prompt: str, task_type: str) -> ExecutionMetrics:
        """Execute a task using the specific reasoning framework."""
        pass
    
    @abstractmethod
    def get_framework_prompt(self, task_prompt: str, task_type: str) -> str:
        """Generate the framework-specific prompt."""
        pass
    
    def _measure_execution(self, func, *args, **kwargs) -> tuple:
        """Measure execution time and memory usage."""
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        return result, execution_time, memory_usage, success, error
    
    def _count_tokens(self, text: str) -> int:
        """Estimate token count (simplified)."""
        # Simple approximation: ~4 characters per token
        return len(text) // 4
    
    def _extract_reasoning_steps(self, response: str) -> List[str]:
        """Extract reasoning steps from the response."""
        # This will be overridden by specific frameworks
        return [response]

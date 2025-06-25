"""
Agent factory for creating different reasoning framework agents.
"""
from typing import Dict, Type, Any
from langchain.llms.base import LLM
from .base_agent import BaseAgent
from .react_agent import ReActAgent
from .cot_agent import CoTAgent
from .tot_agent import ToTAgent


class AgentFactory:
    """Factory class for creating different types of reasoning agents."""
    
    _agent_classes: Dict[str, Type[BaseAgent]] = {
        'react': ReActAgent,
        'cot': CoTAgent,
        'tot': ToTAgent
    }
    
    @classmethod
    def create_agent(cls, framework: str, llm: LLM, **kwargs) -> BaseAgent:
        """Create an agent for the specified framework."""
        framework = framework.lower()
        
        if framework not in cls._agent_classes:
            raise ValueError(f"Unknown framework: {framework}. Available: {list(cls._agent_classes.keys())}")
        
        agent_class = cls._agent_classes[framework]
        return agent_class(llm, **kwargs)
    
    @classmethod
    def get_available_frameworks(cls) -> list:
        """Get list of available reasoning frameworks."""
        return list(cls._agent_classes.keys())
    
    @classmethod
    def register_agent(cls, framework: str, agent_class: Type[BaseAgent]):
        """Register a new agent class for a framework."""
        cls._agent_classes[framework.lower()] = agent_class

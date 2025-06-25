"""
LLM configuration and wrapper utilities.
"""
import os
from typing import Optional, Dict, Any
from langchain.llms.base import LLM
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv


class LLMManager:
    """Manages LLM initialization and configuration."""
    
    def __init__(self):
        load_dotenv()
        self.available_models = {
            'gemini-2.0-flash-lite': self._create_gemini,
            'gemini-2.0-flash': self._create_gemini,
            'gemini-2.5-flash': self._create_gemini
        }
    
    def _create_gemini(self, model_name: str, **kwargs) -> LLM:
        """Create Google Gemini model."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        return GoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=kwargs.get('temperature', 0.3),
            max_output_tokens=kwargs.get('max_tokens', 2048)
        )
    
    def create_llm(self, model_name: str, **kwargs) -> LLM:
        """Create an LLM instance."""
        if model_name not in self.available_models:
            raise ValueError(f"Model {model_name} not supported. Available: {list(self.available_models.keys())}")
        
        return self.available_models[model_name](model_name, **kwargs)
    
    def get_available_models(self) -> list:
        """Get list of available models."""
        return list(self.available_models.keys())
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default LLM configuration from environment."""
        return {
            'model_name': os.getenv('DEFAULT_MODEL'),
            'temperature': float(os.getenv('TEMPERATURE', 0.3)),
            'max_tokens': int(os.getenv('MAX_TOKENS', 2048))
        }
